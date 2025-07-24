from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from database.base import Base

from sqlalchemy import (
    Integer,
    SmallInteger,
    Boolean,
    text,
)


class CountryModel(Base):
    __tablename__ = "state"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    alias: Mapped[str] = mapped_column(String(64), name="alias")
    name: Mapped[str] = mapped_column(String(64), name="name")
    lname: Mapped[str] = mapped_column(String(64), name="lname")
