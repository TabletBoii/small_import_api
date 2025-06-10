import io
from openpyxl import Workbook
from typing import Any, List, Dict

from openpyxl.styles import PatternFill

from file_export.export import Export


class ExportExcel(Export):

    def autofit_columns(self, ws, min_width: int = 10, max_width: int = 50):

        for col in ws.columns:
            col_letter = col[0].column_letter
            lengths = []
            for cell in col:
                if cell.value is not None:
                    lengths.append(len(str(cell.value)))
            if lengths:
                best = max(lengths)
                width = max(min_width, min(best + 2, max_width))
                ws.column_dimensions[col_letter].width = width

    def apply_header_fill(self, ws, header_row: int = 1, fill_color: str = "DDDDDD"):

        fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        for cell in ws[header_row]:
            cell.fill = fill

    def export(self, data: dict, **options):
        wb = Workbook()
        ws = wb.active

        sheet_name = options.get("sheet_name")
        if sheet_name:
            ws.title = sheet_name

        headers = options.get("headers")
        key_header = options.get("key_header")
        file_path = options.get("file_path")
        first_val = next(iter(data.values()), None)
        if first_val is None:
            raise ValueError("data пустой")

        if isinstance(first_val, dict):
            cols = list(first_val.keys())
        elif isinstance(first_val, (list, tuple)):
            cols = [f"Col{i + 1}" for i in range(len(first_val))]
        else:
            raise TypeError("Значения словаря должны быть list, tuple или dict")

        if headers:
            if len(headers) != len(cols):
                raise ValueError("len(headers) != количество полей в данных")
            cols = headers

        ws.append([key_header, *cols])

        for key, val in data.items():
            if isinstance(val, dict):
                row = [key] + [val.get(c) for c in cols]
            else:
                row = [key] + list(val)

            row = [str(cell) if hasattr(cell, 'total_seconds') else cell for cell in row]
            ws.append(row)

        self.autofit_columns(ws)
        self.apply_header_fill(ws)

        wb.save(file_path)
