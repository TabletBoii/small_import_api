from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WebAccessRequestModel(Base):
    __tablename__ = "web_access_request"

    __field_aliases__ = {
        "inc": "ID",
        "user_inc": "ID пользователя",
        "resource_id": "ID ресурса",
        "request_description": "Описание запроса",
        "request_date": "Дата запроса",
        "status": "Статус запроса",
        "rejection_reason": "Причина отказа"
    }

    inc: Mapped[int] = mapped_column(Integer, name="inc", primary_key=True)
    user_inc: Mapped[int] = mapped_column(Integer, name="user_inc")
    resource_id: Mapped[int] = mapped_column(Integer, name="resource_id")
    request_description: Mapped[str] = mapped_column(String(300), name="request_description", nullable=True)
    request_date: Mapped[datetime] = mapped_column(DateTime, name="request_date", default=datetime.now())
    status: Mapped[str] = mapped_column(String(50), name="status")
    rejection_reason: Mapped[str] = mapped_column(String(300), name="rejection_reason", nullable=True)
