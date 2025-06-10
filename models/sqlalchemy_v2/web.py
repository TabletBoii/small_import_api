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
