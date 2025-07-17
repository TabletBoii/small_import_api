from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class AdminPanelAdminAccessModel(Base):
    __tablename__ = "admin_access"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    user_inc: Mapped[int] = mapped_column(Integer, ForeignKey("web_user.inc"), name="user_inc")
    has_access: Mapped[int] = mapped_column(Integer, name="has_access")
