from sqlalchemy import SmallInteger, String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Usnames(Base):
    __tablename__ = "usnames"
    code: Mapped[int] = mapped_column(SmallInteger, primary_key=True, name="code")
    name: Mapped[str] = mapped_column(String(64), nullable=True, name="name")
    alias: Mapped[str] = mapped_column(String(32), nullable=True, name="alias")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=True, name="enabled")
    color: Mapped[int] = mapped_column(Integer, nullable=True, name="color")
    office: Mapped[int] = mapped_column(Integer, nullable=True, name="office")
    department: Mapped[int] = mapped_column(Integer, nullable=True, name="department")

    def __repr__(self) -> str:
        return f"""------------------------------------------------------
code: {self.code!r}
name: {self.name!r}
alias: {self.alias!r}
enabled: {self.enabled!r}
color: {self.color!r}
office: {self.office!r}
department: {self.department!r}
------------------------------------------------------
"""
