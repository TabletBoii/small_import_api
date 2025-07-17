from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebResourceAccessModel(Base):
    __tablename__ = "web_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name="id")
    user_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_user.inc"), name="user_inc")
    web_resource_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_resource.inc"), name="web_resource_inc")
    has_access: Mapped[bool] = mapped_column(Boolean, name="has_access")
