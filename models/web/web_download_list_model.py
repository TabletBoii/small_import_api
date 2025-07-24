from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WebDownloadListModel(Base):
    __tablename__ = "web_download_list"

    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, name="user_id")
    resource_id: Mapped[int] = mapped_column(Integer, name="resource_id")
    file_path: Mapped[str] = mapped_column(String(1024), name="file_path")
    created_date: Mapped[datetime] = mapped_column(DateTime, name="created_date", default=datetime.now())
    in_process: Mapped[bool] = mapped_column(Boolean, name="in_process")
    has_error: Mapped[bool] = mapped_column(Boolean, name="has_error")
    is_downloaded: Mapped[bool] = mapped_column(Boolean, name="is_downloaded")
    params: Mapped[str] = mapped_column(String(1024), name="params", nullable=True)
    error_msg: Mapped[str] = mapped_column(String(1024), name="error_msg", nullable=True)
