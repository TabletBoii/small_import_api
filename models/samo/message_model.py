from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from database.base import Base

from sqlalchemy import (
    Integer,
    SmallInteger,
    Boolean,
    text,
)
from sqlalchemy.dialects.mssql import (
    DATETIME,
    SMALLDATETIME,
    TIMESTAMP as MSSQL_TIMESTAMP,
    BIT,
)


# АККУРАТНО ВЫЗЫВАТЬ ЭТУ МОДЕЛЬ - ОЧ МНОГО ДАННЫХ
class MessageModel(Base):
    __tablename__ = "message"
    inc: Mapped[int] = mapped_column(Integer, primary_key=True, name="inc")
    messagetype: Mapped[int] = mapped_column(Integer, ForeignKey("messagetype.inc"), name="messagetype")
    partner: Mapped[int] = mapped_column(Integer, name="partner")
    subject: Mapped[str | None] = mapped_column(String(510), name="subject", nullable=True)
    text: Mapped[str | None] = mapped_column(String, name="text", nullable=True)
    edate: Mapped[datetime] = mapped_column(DATETIME, name="edate")
    author: Mapped[int] = mapped_column(SmallInteger, name="author")
    user: Mapped[int] = mapped_column(SmallInteger, name="user")
    claim: Mapped[int] = mapped_column(Integer, name="claim")
    status: Mapped[int] = mapped_column(SmallInteger, name="status")
    stamp: Mapped[bytes] = mapped_column(MSSQL_TIMESTAMP, name="stamp")
    incoming: Mapped[bool] = mapped_column(Boolean, name="incoming")
    parent: Mapped[int | None] = mapped_column(Integer, name="parent", nullable=True)
    partpass: Mapped[int | None] = mapped_column(Integer, name="partpass", nullable=True)
    adate: Mapped[datetime] = mapped_column(DATETIME, name="adate")
    email_sent: Mapped[bool] = mapped_column(Boolean, name="email_sent")
    private: Mapped[bool] = mapped_column(Boolean, name="private")
    manager: Mapped[int] = mapped_column(SmallInteger, name="manager")
    message_hash: Mapped[int] = mapped_column(Integer, name="message_hash")
    remind_period: Mapped[int | None] = mapped_column(Integer, name="remind_period", nullable=True)
    remind_datetime: Mapped[datetime | None] = mapped_column(DATETIME, name="remind_datetime", nullable=True)
    origin_message: Mapped[int | None] = mapped_column(Integer, name="origin_message", nullable=True)
    for_incoming_partner: Mapped[bool] = mapped_column(Boolean, name="for_incoming_partner")
    noreply: Mapped[bool] = mapped_column(Boolean, name="noreply")
    importance: Mapped[int] = mapped_column(Integer, name="importance")
    topic: Mapped[int] = mapped_column(Integer, name="topic", nullable=True)
    message_topic: Mapped[int] = mapped_column(Integer, name="message_topic")
    incoming_sent_date: Mapped[datetime | None] = mapped_column(SMALLDATETIME, name="incoming_sent_date", nullable=True)

    def __repr__(self) -> str:
        return f"""------------------------------------------------------
inc: {self.inc!r}
messagetype: {self.messagetype!r}
partner: {self.partner!r}
subject: {self.subject!r}
text: {self.text!r}
edate: {self.edate!r}
author: {self.author!r}
user: {self.user!r}
claim: {self.claim!r}
status: {self.status!r}
stamp: {self.stamp!r}
incoming: {self.incoming!r}
parent: {self.parent!r}
partpass: {self.partpass!r}
adate: {self.adate!r}
email_sent: {self.email_sent!r}
private: {self.private!r}
manager: {self.manager!r}
message_hash: {self.message_hash!r}
remind_period: {self.remind_period!r}
remind_datetime: {self.remind_datetime!r}
origin_message: {self.origin_message!r}
for_incoming_partner: {self.for_incoming_partner!r}
noreply: {self.noreply!r}
importance: {self.importance!r}
topic: {self.topic!r}
message_topic: {self.message_topic!r}
incoming_sent_date: {self.incoming_sent_date!r}
------------------------------------------------------
"""