from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class AdminAuth(Base):
    __tablename__ = "admin_auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, name="id")
    username: Mapped[str] = mapped_column(String(255), name="username")
    password_hashed: Mapped[str] = mapped_column(String(255), name="password_hashed")
    description: Mapped[str] = mapped_column(String(255), name="description", nullable=True)
