from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from database.base import Base

from sqlalchemy import (
    Integer,
    SmallInteger,
    Boolean,
    text,
)


class WebUser(Base):
    __tablename__ = "web_user"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(64), name="name")
    hashed_password: Mapped[str] = mapped_column(String(200), name="hashed_password")
    description: Mapped[str | None] = mapped_column(String(200), name="description", nullable=True)


class WebResource(Base):
    __tablename__ = "web_resource"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(50), name="name")
    type: Mapped[int] = mapped_column(Integer, name="type")


class WebResourceType(Base):
    __tablename__ = "web_resource_type"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(50), name="name")


class WebResourceAccess(Base):
    __tablename__ = "web_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name="id")
    user_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_user.inc"), name="user_inc")
    web_resource_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_resource.inc"), name="web_resource_inc")
    has_access: Mapped[bool] = mapped_column(Boolean, name="has_access")


class WebTemplate(Base):
    __tablename__ = "web_template"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String, name="name")
    web_resource_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_resource.inc"), name="web_resource_inc")
    user_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_user.inc"), name="user_inc")


class WebTemplateItems(Base):
    __tablename__ = "web_template_items"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    field: Mapped[str] = mapped_column(String, name="field")
    web_template: Mapped[int] = mapped_column(Integer, ForeignKey("web_template.inc"), name="web_template")


class WebDirectionList(Base):
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
