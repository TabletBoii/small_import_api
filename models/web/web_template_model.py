from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebTemplateModel(Base):
    __tablename__ = "web_template"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String, name="name")
    web_resource_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_resource.inc"), name="web_resource_inc")
    user_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_user.inc"), name="user_inc")
