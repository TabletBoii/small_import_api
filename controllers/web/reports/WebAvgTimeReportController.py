import asyncio
import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from controllers.abstract_file_generator_controller import AbstractFileGeneratorController
from dao.samo import message_dao, usnames_dao
from dao.samo.department_dao import get_departments_by_name, get_department_name_by_id
from dao.web.department_schedule_dao import get_department_schedule
from database.sessions import KOMPAS_SESSION_FACTORY, WEB_SESSION_FACTORY
from dataclasses_custom.schedule import WorkingHours
from utils.file_export.excel_export import ExportExcel

week_days_by_number = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6
}


class WebAvgTimeReport(AbstractFileGeneratorController):
    async def _streaming_run(self):
        pass

    def __init__(
            self,
            date_from: str,
            date_till: str,
            departments: List[str],
            report_type: Optional[str],
            file_path: str,
            download_id
    ):
        self.session_factory: async_sessionmaker = None
        self.name_pattern = "INTERNET"  # TODO: это так не должно быть. Нужно понять, что делать с клиентами, которые не INTERNET like
        self.department_list = departments
        self.department_id_list = None
        self.date_periods = [
            date_from,
            date_till
        ]
        self.report_type = report_type
        self.engine = None
        self.raw_data_per_department = None
        self.file_path = file_path
        self.download_id = download_id

    def set_session(self, session_factory):
        self.session_factory = session_factory

    async def dispose_engine(self):
        if self.engine:
            await self.engine.dispose()

    @staticmethod
    async def get_department_ids(department_list: List[str]):
        async with KOMPAS_SESSION_FACTORY() as session:
            return await get_departments_by_name(session, department_list)

    async def process_raw_msg_by_department(
            self,
            department_id: int,
    ):

        async with KOMPAS_SESSION_FACTORY() as session:
            raw_messages = await message_dao.get_raw_msg_list(
                session=session,
                date_period=self.date_periods,
                department_id=department_id
            )

        aggregated_message_dict_by_claim = defaultdict(list)
        for message in raw_messages:
            claim_id = message[0]
            aggregated_message_dict_by_claim[claim_id].append(message)

        return aggregated_message_dict_by_claim

    async def report_data_base(self):
        coros = [
            self.process_raw_msg_by_department(dept_id)
            for dept_id in self.department_id_list
        ]

        per_dept_results = await asyncio.gather(*coros)

        return {
            dept_id: result_dict
            for dept_id, result_dict in zip(self.department_id_list, per_dept_results)
        }

    async def agg_report(self) -> dict[str, list[int, int, int]]:

        async with self.session_factory() as session:
            internet_usnames_code_list = await usnames_dao.get_id_by_similar_name(
                session=session,
                name_pattern=self.name_pattern
            )

        async with WEB_SESSION_FACTORY() as session:
            department_schedule_dict = await get_department_schedule(session)
        department_schedule = {}
        for schedule in department_schedule_dict:
            department_schedule[schedule["department_inc"]] = [0, 0, 0, 0, 0, 0, 0]

        for schedule in department_schedule_dict:
            department_schedule[schedule["department_inc"]][week_days_by_number[schedule["week_day"]]] = WorkingHours(
                schedule["start_time"].hour,
                schedule["end_time"].hour
            )
        print(department_schedule)
        for key, value in department_schedule.items():
            if value[6] == 0:
                department_schedule[key].pop(6)

        resulted_collection: Dict[str, List[int, int, int]] = {}
        for dept_id, aggregated_message_dict_by_claim in self.raw_data_per_department.items():
            avg_time = timedelta()
            avg_time_count = 0
            incoming_msg_count = 0
            outcoming_msg_count = 0
            for claim_id, message_list in aggregated_message_dict_by_claim.items():
                message_author_sequence_list = []
                for index, message in enumerate(message_list):
                    """
                        Исключаю робота
                    """
                    if message[1] == 3:
                        continue

                    """
                        Выбираю только клиентов с ником INTERNET
                    """
                    if message[1] in internet_usnames_code_list:
                        message_author_sequence_list.append(index)
                        incoming_msg_count += 1
                        continue

                    if len(message_author_sequence_list) == 0:
                        continue

                    for author_message_index in message_author_sequence_list:
                        """
                            Если ответ не клиенту с ником INTERNET - скипаем 
                            (ранее я уже выбрал сообщения, автором которых является только INTERNET,
                            Но здесь скипаются сообщения, получателем которых является не INTERNET
                        """
                        if message[2] not in internet_usnames_code_list:
                            continue

                        client_msg_date = message_list[author_message_index][3]
                        employee_response_date: datetime = message[3]
                        client_msg_weekday = client_msg_date.weekday()
                        employee_msg_weekday = employee_response_date.weekday()
                        if len(department_schedule[dept_id]) == 6 and client_msg_weekday == 6:
                            next_day = client_msg_date + timedelta(days=1)
                            adate_diff = (employee_response_date
                                          - next_day.replace(
                                        hour=department_schedule[dept_id][0].begin,
                                        minute=0,
                                        second=0,
                                        microsecond=0)
                                          )
                        else:
                            if len(department_schedule[dept_id]) == 6 and employee_msg_weekday == 6:
                                continue
                            if (department_schedule[dept_id][employee_msg_weekday].begin > employee_response_date.hour
                                    or employee_response_date.hour >= department_schedule[dept_id][
                                        employee_msg_weekday].end):
                                ...
                                continue
                            """
                                ВАЖНО - исходя из нынешней логики, каждый отдел должен иметь как минимум 6 рабочих дней
                            """

                            if client_msg_date.hour < department_schedule[dept_id][client_msg_weekday].begin:
                                adate_diff = employee_response_date - datetime(
                                    year=client_msg_date.year,
                                    month=client_msg_date.month,
                                    day=client_msg_date.day,
                                    hour=department_schedule[dept_id][client_msg_weekday].begin,
                                    minute=0,
                                    second=0
                                )
                            elif client_msg_date.hour >= department_schedule[dept_id][client_msg_weekday].end:
                                next_day = client_msg_date + timedelta(days=1)
                                adate_diff = (employee_response_date
                                              - next_day.replace(
                                            hour=department_schedule[dept_id][employee_msg_weekday].begin,
                                            minute=0,
                                            second=0,
                                            microsecond=0)
                                              )
                            else:
                                adate_diff = employee_response_date - client_msg_date
                                # TODO заявка 1275722, ID сообщений: 6456240, 6456332, 6458931
                        if adate_diff >= timedelta(hours=4):
                            ...
                        else:
                            avg_time_count += 1
                            avg_time += adate_diff
                            outcoming_msg_count += 1

                    message_author_sequence_list.clear()
            async with self.session_factory() as session:
                dept_name = await get_department_name_by_id(session, dept_id)
            resulted_collection[dept_name] = [avg_time / avg_time_count if avg_time_count != 0 else 0, incoming_msg_count, outcoming_msg_count]
        return resulted_collection

    async def generate_excel_bytes(
            self,
            data,
            header
    ):
        return ExportExcel().export(
            data=data,
            headers=header,
            key_header="Департамент",
            sheet_name="Отчет по среднему времени ответа (агрегированный)",
            file_path=self.file_path
        )

    async def _run(self):
        try:
            self.department_id_list = await self.get_department_ids(self.department_list)
            self.raw_data_per_department = await self.report_data_base()
            match self.report_type:
                case "Отчет по среднему времени ответа (агрегированный)":
                    report_result = await self.agg_report()

                    await self.generate_excel_bytes(
                        report_result,
                        (
                            "Среднее время ответа, мин",
                            "Кол-во входящих сообщений",
                            "Кол-во исходящих сообщений"
                        )
                    )

                case "AvgTimeReport":
                    ...

                case "AnomalyMsgReport":
                    ...

                case "MoreThanFourHoursAnswerReport":
                    ...
        except Exception as e:
            raise e
