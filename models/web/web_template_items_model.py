from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebTemplateItemsModel(Base):
    __tablename__ = "web_template_items"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    field: Mapped[str] = mapped_column(String, name="field")
    web_template: Mapped[int] = mapped_column(Integer, ForeignKey("web_template.inc"), name="web_template")
