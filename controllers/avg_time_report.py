import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy.ext.asyncio import async_sessionmaker

from custom_types.custom_types import ClaimID, Sender, Recipient, MsgDate
from dao.samo import message_dao, usnames_dao
from dataclasses_custom.dev.user_avg_entries import UserAvgEntryDataclass, ClaimDataDataclass, MessageDataclass
from dataclasses_custom.schedule import WorkingHours
from pydantic_models.request_models import AvgTimeReportModel

department_schedule = {
    13: [
        WorkingHours(9, 21),
        WorkingHours(9, 21),
        WorkingHours(9, 21),
        WorkingHours(9, 21),
        WorkingHours(9, 21),
        WorkingHours(10, 17),
        WorkingHours(10, 16)
    ]
}


class AvgTimeReport:
    def __init__(self, avg_time_report_params: list[AvgTimeReportModel]):
        self.session_factory: async_sessionmaker = None
        self.avg_time_report_params = avg_time_report_params[0]
        self.name_pattern = "INTERNET"  # TODO: это так не должно быть
        self.department_id = avg_time_report_params[0].department_list[0]
        self.date_periods = [
            datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            for date in self.avg_time_report_params.date_periods
        ]
        self.engine = None

    def set_session(self, session_factory):
        self.session_factory = session_factory

    @staticmethod
    async def build_employee_message_list(message_list, message, msd, claim_id, last_message_index, avg_time):
        if message[1] not in msd.keys():
            msd[message[1]] = {}
            msd[message[1]][claim_id] = [
                UserAvgEntryDataclass(
                    message_list=[ClaimDataDataclass(
                        initial_msg=MessageDataclass(
                            sender=message_list[last_message_index][1],
                            recipient=message_list[last_message_index][2],
                            msg_date=message_list[last_message_index][3]
                        ),
                        response_msg=MessageDataclass(
                            sender=message[1],
                            recipient=message[2],
                            msg_date=message[3]
                        ),
                        avgTime=avg_time
                    )]
                )
            ]
        else:
            if claim_id not in msd[message[1]]:
                msd[message[1]][claim_id] = [
                    UserAvgEntryDataclass(
                        message_list=[ClaimDataDataclass(
                            initial_msg=MessageDataclass(
                                sender=message_list[last_message_index][1],
                                recipient=message_list[last_message_index][2],
                                msg_date=message_list[last_message_index][3]
                            ),
                            response_msg=MessageDataclass(
                                sender=message[1],
                                recipient=message[2],
                                msg_date=message[3]
                            ),
                            avgTime=avg_time
                        )]
                    )
                ]
            else:
                msd[message[1]][claim_id].append(
                    UserAvgEntryDataclass(
                        message_list=[ClaimDataDataclass(
                            initial_msg=MessageDataclass(
                                sender=message_list[last_message_index][1],
                                recipient=message_list[last_message_index][2],
                                msg_date=message_list[last_message_index][3]
                            ),
                            response_msg=MessageDataclass(
                                sender=message[1],
                                recipient=message[2],
                                msg_date=message[3]
                            ),
                            avgTime=avg_time
                        )]
                    )
                )

    async def dispose_engine(self):
        if self.engine:
            await self.engine.dispose()

    async def run(self):
        async with self.session_factory() as session:
            claim_count_dict: Dict[int, int] = await message_dao.get_claim_count_by_department_and_period(
                session=session,
                department_id=self.department_id,  # TODO: Переделать выборку с одного департамента на список
                date_period=self.date_periods
            )

            claim_list = [claim_id for claim_id in claim_count_dict.keys()]

            distinct_message_by_claim_list = await message_dao.get_first_claims_message(
                session=session,
                claim_list=claim_list,
                department_id=self.department_id
            )

            internet_usnames_code_list = await usnames_dao.get_id_by_similar_name(
                session=session,
                name_pattern=self.name_pattern
            )
        distinct_message_by_claim_list_filtered = [
            message for message in distinct_message_by_claim_list
            if message.author in internet_usnames_code_list
        ]

        claim_list_filtered = [
            message[0] for message in distinct_message_by_claim_list_filtered
        ]

        async with self.session_factory() as session:

            raw_messages: List[
                Tuple[
                    ClaimID,
                    Sender,
                    Recipient,
                    MsgDate
                ]
            ] = await message_dao.get_by_claims_and_period_and_department(
                session=session,
                claim_list=claim_list_filtered,
                date_period=self.date_periods,
                department_id=self.department_id
            )

        MessageTuple = Tuple[ClaimID, Sender, Recipient, MsgDate]

        aggregated_message_dict_by_claim: Dict[
            ClaimID,
            List[MessageTuple]
        ] = defaultdict(list)

        for message in raw_messages:
            aggregated_message_dict_by_claim[message[0]].append(message)

        user_avg_time_dict: Dict[int, Dict[int, UserAvgEntryDataclass]] = {}  # Список ответов
        non_working_hours_dict: Dict[int, Dict[int, UserAvgEntryDataclass]] = {}  # Список ответов в нерабочее время
        anomaly_msd: Dict[int, Dict[int, UserAvgEntryDataclass]] = {}  # Список ответов с высоким avg_time

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
                    employee_response_date: datetime.datetime = message[3]
                    client_msg_weekday = client_msg_date.weekday()
                    employee_msg_weekday = employee_response_date.weekday()

                    if (department_schedule[self.department_id][employee_msg_weekday].begin > employee_response_date.hour
                            or employee_response_date.hour >= department_schedule[self.department_id][
                                employee_msg_weekday].end):
                        ...
                        # await self.build_employee_message_list(
                        #     message_list=message_list,
                        #     message=message,
                        #     msd=non_working_hours_dict,
                        #     claim_id=claim_id,
                        #     last_message_index=author_message_index,
                        #     avg_time=datetime.timedelta()
                        # )
                        continue

                    if client_msg_date.hour < department_schedule[self.department_id][client_msg_weekday].begin:
                        adate_diff = employee_response_date - datetime.datetime(
                            year=client_msg_date.year,
                            month=client_msg_date.month,
                            day=client_msg_date.day,
                            hour=department_schedule[self.department_id][client_msg_weekday].begin,
                            minute=0,
                            second=0
                        )
                    elif client_msg_date.hour >= department_schedule[self.department_id][client_msg_weekday].end:
                        next_day = client_msg_date + datetime.timedelta(days=1)
                        adate_diff = (employee_response_date
                                      - next_day.replace(
                                    hour=department_schedule[self.department_id][employee_msg_weekday].begin,
                                    minute=0,
                                    second=0,
                                    microsecond=0)
                                      )
                    else:
                        adate_diff = employee_response_date - client_msg_date
                        # TODO заявка 1275722, ID сообщений: 6456240, 6456332, 6458931
                    if adate_diff >= datetime.timedelta(hours=4):
                        ...
                        # await self.build_employee_message_list(
                        #     message_list=message_list,
                        #     message=message,
                        #     msd=anomaly_msd,
                        #     claim_id=claim_id,
                        #     last_message_index=author_message_index,
                        #     avg_time=adate_diff
                        # )
                    else:
                        await self.build_employee_message_list(
                            message_list=message_list,
                            message=message,
                            msd=user_avg_time_dict,
                            claim_id=claim_id,
                            last_message_index=author_message_index,
                            avg_time=adate_diff
                        )
                message_author_sequence_list.clear()
        return user_avg_time_dict
