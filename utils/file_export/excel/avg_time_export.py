import datetime
import io
import os
from typing import Dict, List, Any

from openpyxl.workbook import Workbook

from dao.samo import usnames_dao
from database.session import SessionLocal1
from dataclasses_custom.dev.user_avg_entries import UserAvgEntryDataclass
from utils.file_export.excel_export import ExportExcel


class AvgTimeExport(ExportExcel):
    def __init__(self,
                 data: Dict[int, Dict[int, List[UserAvgEntryDataclass]]],
                 dir_name: str,
                 file_name: str,
                 headers: List[str] | None = None):
        self._data = data
        self._dir_name = dir_name
        self._file_name = file_name
        self._headers = headers or ["claim_id", "message", "Sender", "Recipient", "MsgDate", "AvgTime"]
        super().__init__()

    def export(self, data: List[Dict[str, Any]], **options) -> bytes:
        raise NotImplementedError("Use run() for multi-sheet export")

    async def run(self) -> None:
        wb = Workbook()
        async with SessionLocal1() as session:
            employee_dict: Dict[int, str] = await usnames_dao.get_name_by_id_dict(
                session=session,
                id_list=self._data.keys()
            )

        first_sheet = True

        for employee_id, claims in self._data.items():
            sheet_title = f"employee_{employee_id}"
            if first_sheet:
                ws = wb.active
                ws.title = sheet_title
                first_sheet = False
            else:
                ws = wb.create_sheet(title=sheet_title)

            ws.append(self._headers)
            count = 0
            avg_time = datetime.timedelta()
            for claim_id, entries in claims.items():
                for entry in entries:
                    for cd in entry.message_list:
                        ws.append([
                            claim_id,
                            f"msg{1}",
                            cd.initial_msg.sender,
                            employee_dict[cd.initial_msg.recipient] if cd.initial_msg.recipient in employee_dict.keys() else cd.initial_msg.recipient,
                            cd.initial_msg.msg_date,
                            cd.avgTime,
                        ])
                        ws.append([
                            claim_id,
                            f"msg{2}",
                            employee_dict[cd.response_msg.sender] if cd.response_msg.sender in employee_dict.keys() else cd.response_msg.sender,
                            cd.response_msg.recipient,
                            cd.response_msg.msg_date,
                        ])
                        count += 1
                        avg_time += cd.avgTime
            ws.append([
                "",
                "",
                "",
                "",
                "Total Avg Time",
                avg_time / count
            ])
        if not os.path.exists(os.path.join(os.getcwd(), self._dir_name)):
            os.makedirs(self._dir_name)
        # Сохраняем в файл
        with open(f"./{self._dir_name}/"+self._file_name, "wb") as f:
            stream = io.BytesIO()
            wb.save(stream)
            f.write(stream.getvalue())
