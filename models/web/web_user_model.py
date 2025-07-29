from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebUserModel(Base):
    __tablename__ = "web_user"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(64), name="name")
    hashed_password: Mapped[str] = mapped_column(String(200), name="hashed_password", nullable=True)
    description: Mapped[str | None] = mapped_column(String(200), name="description", nullable=True)
    microsoft_email: Mapped[str] = mapped_column(String(100), name="microsoft_email", unique=True, nullable=True)
    microsoft_oid: Mapped[str] = mapped_column(String(100), name="microsoft_oid", unique=True, nullable=True)
