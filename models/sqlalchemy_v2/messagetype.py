from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.base import Base


class MessageType(Base):
    __tablename__ = "messagetype"

    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    name: Mapped[str | None] = mapped_column(String(128), name="name", nullable=True)
    lname: Mapped[str | None] = mapped_column(String(128), name="lname", nullable=True)
    department: Mapped[Integer | None] = mapped_column(Integer, ForeignKey("department.inc"), name="department", nullable=True)
    private: Mapped[bool] = mapped_column(Boolean, name="private")
    note_html: Mapped[str] = mapped_column(String, name="note_html", nullable=True)
    attach_required: Mapped[bool] = mapped_column(Boolean, name="attach_required")
    default_from_department: Mapped[bool] = mapped_column(Boolean, name="default_for_department")