from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from database.base import Base

from sqlalchemy import (
    Integer,
    SmallInteger,
    Boolean,
    text,
)


class Department(Base):
    __tablename__ = "department"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(64), name="name")
    lname: Mapped[str] = mapped_column(String(64), name="lname")
    phones: Mapped[str | None] = mapped_column(String(255), name="phones", nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), name="email", nullable=True)
