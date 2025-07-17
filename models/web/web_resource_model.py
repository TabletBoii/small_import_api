from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebResourceModel(Base):
    __tablename__ = "web_resource"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(50), name="name")
    type: Mapped[int] = mapped_column(Integer, name="type")
    name_cirill: Mapped[str] = mapped_column(String(200), name="name_cirill")
    description: Mapped[str] = mapped_column(String(200), name="description")
