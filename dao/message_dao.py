from datetime import datetime
from typing import Sequence, Tuple, List, Dict, Any

from sqlalchemy import select, join, func, literal_column, true, text, bindparam, Row, asc
from sqlalchemy.ext.asyncio import AsyncSession

from custom_types.custom_types import ClaimID, Sender, Recipient, MsgDate
from models.sqlalchemy_v2.department import Department
from models.sqlalchemy_v2.message import Message
from models.sqlalchemy_v2.messagetype import MessageType


async def get_top_1000(session: AsyncSession) -> Sequence[Message]:
    stmt = select(Message).limit(1000).execution_options(caller="message.get_top_1000")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_claim_inc(session: AsyncSession, claim_inc: int) -> Sequence[Message]:
    stmt = select(Message).where(Message.claim == claim_inc).execution_options(caller="message.get_by_claim_inc")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_date_period(session: AsyncSession, date_period: Tuple[datetime, datetime]) -> Sequence[Message]:
    stmt = (select(Message)
            .where(Message.adate >= date_period[0])
            .where(Message.adate <= date_period[1])
            .execution_options(caller="message.get_by_date_period")
            )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_claims_and_period_and_department(
    session: AsyncSession,
    claim_list: List[int],
    date_period: List[datetime],
    department_id: int
) -> list[tuple[ClaimID, Sender, Recipient, MsgDate]]:
    jt = join(
        Message, MessageType,
        Message.messagetype == MessageType.inc
    )
    jd = join(
        jt, Department,
        MessageType.department == Department.inc
    )

    stmt = (select(Message.claim, Message.author, Message.user, Message.adate)
            .select_from(jd)
            .where(Department.inc == department_id)
            .where(Message.adate >= date_period[0])
            .where(Message.adate <= date_period[1])
            .where(Message.claim.in_(claim_list))
            .order_by(asc(Message.adate))
            .execution_options(caller="message.get_by_claims_and_period_and_department")
            )
    result = await session.execute(stmt)
    return result.all()


async def get_claim_count_by_department_and_period(
        session: AsyncSession,
        department_id: int,
        date_period: List[datetime]
) -> Dict[int, int]:
    jt = join(
        Message, MessageType,
        Message.messagetype == MessageType.inc
    )
    jd = join(
        jt, Department,
        MessageType.department == Department.inc
    )

    stmt = (
        select(
            Message.claim,
            func.count(Message.inc).label("cnt")
        )
        .select_from(jd)
        .where(Department.inc == department_id)
        .where(Message.adate.between(date_period[0], date_period[1]))
        .group_by(Message.claim)
        .order_by(Message.claim)
        .execution_options(caller="message.get_claim_count_by_department_and_period")
    )

    result = await session.execute(stmt)

    return dict(result.all())


async def get_overall_claim_count_by_claim_list(
        session: AsyncSession,
        claim_list: List[int]
) -> Dict[int, int]:
    stmt = (
        select(
            Message.claim,
            func.count(Message.inc).label("cnt")
        )
        .where(Message.claim.in_(claim_list))
        .group_by(Message.claim)
        .order_by(Message.claim)
        .execution_options(caller="message.get_overall_claim_count_by_claim_list")
    )

    result = await session.execute(stmt)
    return dict(result.all())


async def get_by_department_and_date(
        session: AsyncSession,
        department_id: int,
        date_period: Tuple[datetime, datetime]
) -> Sequence[Message]:
    jt = join(Message, MessageType,
              Message.messagetype == MessageType.inc)
    jd = join(jt, Department,
              MessageType.department == Department.inc)

    stmt = (
        select(Message)
        .select_from(jd)
        .where(Department.inc == department_id)
        .where(Message.adate.between(date_period[0], date_period[1]))
        .order_by(Message.inc)
        .execution_options(caller="message.message.get_by_department_and_date")
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_first_claims_message(session: AsyncSession, claim_list: List[int], department_id: int):
    stmt = text(
        """
        WITH FirstMsg AS (
          SELECT
            m.claim,
            m.author,
            au.name        AS author_name,
            m.[user],
            uu.name        AS user_name,
            mt.department,
            mt.inc         AS messagetype_inc,
            mt.name        AS messagetype_name,
            ROW_NUMBER() OVER (
              PARTITION BY m.claim
              ORDER BY m.adate ASC
            ) AS rn
          FROM dbo.message    AS m
          INNER JOIN dbo.messagetype AS mt
            ON mt.inc = m.messagetype
           AND mt.department = :dept_id
          LEFT JOIN dbo.usnames AS au
            ON au.code = m.author
          LEFT JOIN dbo.usnames AS uu
            ON uu.code = m.[user]
          WHERE m.claim IN :claims
        )
        SELECT
          claim,
          author,
          author_name,
          [user],
          user_name,
          department,
          messagetype_inc,
          messagetype_name
        FROM FirstMsg
        WHERE rn = 1
        ORDER BY claim;

        """
    ).execution_options(caller="message.message.get_first_claims_message").bindparams(
        bindparam("claims", expanding=True),  # превращает IN (:claims_1, :claims_2,…)
        bindparam("dept_id"),
    )

    result = await session.execute(
        stmt,
        {"claims": claim_list, "dept_id": department_id},
    )
    return result.all()
