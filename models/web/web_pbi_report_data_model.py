from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WebPbiReportDataModel(Base):
    __tablename__ = "web_pbi_report_data"

    __field_aliases__ = {
        "id": "ID",
        "workspace_id": "ID рабочей области",
        "report_id": "ID отчета",
        "resource_id": "Ресурс",
    }

    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, name="workspace_id")
    report_id: Mapped[str] = mapped_column(String, name="report_id")
    resource_id: Mapped[int] = mapped_column(Integer, name="resource_id")
