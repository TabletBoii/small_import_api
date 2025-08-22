from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from models.base import Base


class WebPbiTelemetryModel(Base):
    __tablename__ = "web_powerbi_telemetry"

    __table_args__ = {'implicit_returning': False}

    inc: Mapped[int] = mapped_column(Integer, name="inc", primary_key=True)
    user_inc: Mapped[int] = mapped_column(Integer, name="user_inc")
    report_id: Mapped[int] = mapped_column(Integer, name="report_id")
    type: Mapped[str] = mapped_column(String, name="type")
    page_title: Mapped[str] = mapped_column(Integer, name="page_title", nullable=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, name="create_date")
