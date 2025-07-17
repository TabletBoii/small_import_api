from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Partner(Base):
    __tablename__ = "partner"

    inc: Mapped[int] = mapped_column(Integer, name="inc", primary_key=True)
    name: Mapped[str] = mapped_column(Integer, name="name")
