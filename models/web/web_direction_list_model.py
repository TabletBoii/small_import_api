from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebDirectionListModel(Base):
    __tablename__ = "web_direction_list"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    airline_name: Mapped[str] = mapped_column(String, name="airline_name", nullable=True)
    country_of_departure: Mapped[str] = mapped_column(String, name="country_of_departure", nullable=True)
    country_of_arrival: Mapped[str] = mapped_column(String, name="country_of_arrival", nullable=True)
    town_of_departure: Mapped[str] = mapped_column(String, name="town_of_departure", nullable=True)
    town_of_arrival: Mapped[str] = mapped_column(String, name="town_of_arrival", nullable=True)
    town_of_departure_alias: Mapped[str] = mapped_column(String, name="town_of_departure_alias")
    town_of_arrival_alias: Mapped[str] = mapped_column(String, name="town_of_arrival_alias")
    airline_alias: Mapped[str] = mapped_column(String, name="airline_alias", nullable=True)
    status: Mapped[str] = mapped_column(String, name="status")
    flight_alias: Mapped[str] = mapped_column(String, name="flight_alias", nullable=True)
