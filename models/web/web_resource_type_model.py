from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebResourceTypeModel(Base):
    __tablename__ = "web_resource_type"

    __field_aliases__ = {
        "inc": "ID",
        "name": "Название",
        "name_cirill": "Название(кир.)"
    }

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str] = mapped_column(String(50), name="name")
    name_cirill: Mapped[str] = mapped_column(String(100), name="name_cirill")
