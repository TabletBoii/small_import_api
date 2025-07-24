from datetime import datetime
from typing import Sequence, Tuple, List, Dict

from sqlalchemy import select, join, func, text, bindparam, asc
from sqlalchemy.ext.asyncio import AsyncSession

from custom_types.custom_types import ClaimID, Sender, Recipient, MsgDate
from models.samo.department_model import DepartmentModel
from models.samo.message_model import MessageModel
from models.samo.messagetype_model import MessageTypeModel


async def get_top_1000(session: AsyncSession) -> Sequence[MessageModel]:
    stmt = select(MessageModel).limit(1000).execution_options(caller="message.get_top_1000")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_claim_inc(session: AsyncSession, claim_inc: int) -> Sequence[MessageModel]:
    stmt = select(MessageModel).where(MessageModel.claim == claim_inc).execution_options(caller="message.get_by_claim_inc")
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_by_date_period(session: AsyncSession, date_period: Tuple[datetime, datetime]) -> Sequence[MessageModel]:
    stmt = (select(MessageModel)
            .where(MessageModel.adate >= date_period[0])
            .where(MessageModel.adate <= date_period[1])
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
        MessageModel, MessageTypeModel,
        MessageModel.messagetype == MessageTypeModel.inc
    )
    jd = join(
        jt, DepartmentModel,
        MessageTypeModel.department == DepartmentModel.inc
    )

    stmt = (select(MessageModel.claim, MessageModel.author, MessageModel.user, MessageModel.adate)
            .select_from(jd)
            .where(DepartmentModel.inc == department_id)
            .where(MessageModel.adate >= date_period[0])
            .where(MessageModel.adate <= date_period[1])
            .where(MessageModel.claim.in_(claim_list))
            .order_by(asc(MessageModel.adate))
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
        MessageModel, MessageTypeModel,
        MessageModel.messagetype == MessageTypeModel.inc
    )
    jd = join(
        jt, DepartmentModel,
        MessageTypeModel.department == DepartmentModel.inc
    )

    stmt = (
        select(
            MessageModel.claim,
            func.count(MessageModel.inc).label("cnt")
        )
        .select_from(jd)
        .where(DepartmentModel.inc == department_id)
        .where(MessageModel.adate.between(date_period[0], date_period[1]))
        .group_by(MessageModel.claim)
        .order_by(MessageModel.claim)
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
            MessageModel.claim,
            func.count(MessageModel.inc).label("cnt")
        )
        .where(MessageModel.claim.in_(claim_list))
        .group_by(MessageModel.claim)
        .order_by(MessageModel.claim)
        .execution_options(caller="message.get_overall_claim_count_by_claim_list")
    )

    result = await session.execute(stmt)
    return dict(result.all())


async def get_by_department_and_date(
        session: AsyncSession,
        department_id: int,
        date_period: Tuple[datetime, datetime]
) -> Sequence[MessageModel]:
    jt = join(MessageModel, MessageTypeModel,
              MessageModel.messagetype == MessageTypeModel.inc)
    jd = join(jt, DepartmentModel,
              MessageTypeModel.department == DepartmentModel.inc)

    stmt = (
        select(MessageModel)
        .select_from(jd)
        .where(DepartmentModel.inc == department_id)
        .where(MessageModel.adate.between(date_period[0], date_period[1]))
        .order_by(MessageModel.inc)
        .execution_options(caller="message.message.get_by_department_and_date")
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_first_claims_message(session: AsyncSession, department_id: int, date_period):
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
              WHERE m.claim IN (
				SELECT DISTINCT msg_inner.claim
				FROM message as msg_inner
				LEFT JOIN messagetype as mtype_inner ON mtype_inner.inc = msg_inner.messagetype
				LEFT JOIN department as dept_inner ON dept_inner.inc = mtype_inner.department
				WHERE dept_inner.inc = :dept_id AND msg_inner.adate BETWEEN :date_beg AND :date_end
			  )
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
        bindparam("date_beg"),
        bindparam("date_end"),
        bindparam("dept_id"),
    )

    result = await session.execute(
        stmt,
        {"date_beg": date_period[0], "date_end": date_period[1], "dept_id": department_id},
    )
    return result.all()


async def get_raw_msg_list(session: AsyncSession, department_id: int, date_period):
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
            WHERE m.claim IN (
                SELECT DISTINCT msg_inner.claim
                FROM message as msg_inner
                LEFT JOIN messagetype as mtype_inner ON mtype_inner.inc = msg_inner.messagetype
                LEFT JOIN department as dept_inner ON dept_inner.inc = mtype_inner.department
                WHERE dept_inner.inc = :dept_id AND msg_inner.adate BETWEEN :date_beg AND :date_end
            )
        )
        
        SELECT msg_final.claim, msg_final.author, msg_final.[user], msg_final.adate
        FROM message AS msg_final
        LEFT JOIN messagetype as msg_type_final ON msg_type_final.inc = msg_final.messagetype
        LEFT JOIN department as dpt_final ON dpt_final.inc = msg_type_final.department
        WHERE  dpt_final.inc = :dept_id
        AND msg_final.claim IN (
            SELECT
                claim
            FROM FirstMsg
            WHERE rn = 1 AND author_name LIKE '%INTERNET%'
        )
        AND
        msg_final.adate BETWEEN :date_beg AND :date_end
        
        
        ORDER BY msg_final.adate ASC

        """  # TODO: Здесь прописаны только INTERNET
    ).execution_options(caller="message.message.get_first_claims_message").bindparams(
        bindparam("date_beg"),
        bindparam("date_end"),
        bindparam("dept_id"),
    )

    result = await session.execute(
        stmt,
        {"date_beg": date_period[0], "date_end": date_period[1], "dept_id": department_id},
    )
    return result.all()
