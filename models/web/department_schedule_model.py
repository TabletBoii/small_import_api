from datetime import time

from sqlalchemy import Integer, String, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class DepartmentScheduleModel(Base):
    __tablename__ = "department_schedule"

    __field_aliases__ = {
        "inc": "ID",
        "department_inc": "ID департамента",
        "week_day": "День недель",
        "start_time": "Дата начала",
        "end_time": "Дата окончания"
    }

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    department_inc: Mapped[int] = mapped_column(Integer, name="department_inc")
    week_day: Mapped[str] = mapped_column(String(30), name="week_day")
    start_time: Mapped[time] = mapped_column(Time, name="start_time")
    end_time: Mapped[time] = mapped_column(Time, name="end_time")
