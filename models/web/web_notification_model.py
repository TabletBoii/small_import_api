from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WebNotificationModel(Base):
    __tablename__ = "web_notification"

    inc: Mapped[int] = mapped_column(Integer, name="inc", primary_key=True)
    user_inc: Mapped[int] = mapped_column(Integer, name="user_inc")
    message: Mapped[str] = mapped_column(String(200), name="message")
    category: Mapped[str] = mapped_column(String(50), name="category", default="info")
    created_at: Mapped[datetime] = mapped_column(DateTime, name="created_at", server_default=func.now())
    read_at: Mapped[datetime] = mapped_column(DateTime, name="read_at", nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, name="expires_at", nullable=True)
