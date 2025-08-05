from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dao.web.resource_dao import get_web_resource_by_name
from models.web.web_pbi_report_data_model import WebPbiReportDataModel


async def get_pbi_report_data_by_resource_id(session: AsyncSession, resource_id: int) -> WebPbiReportDataModel:
    stmt = (
        select(WebPbiReportDataModel).where(WebPbiReportDataModel.resource_id == resource_id)
    )

    result = await session.execute(stmt)

    return result.scalars().first()


async def get_pbi_report_data_by_resource_name(session: AsyncSession, resource_name: str) -> WebPbiReportDataModel:
    resource_result = await get_web_resource_by_name(session, resource_name)
    resource_id = resource_result.inc
    stmt = (
        select(WebPbiReportDataModel).where(WebPbiReportDataModel.resource_id == resource_id)
    )

    result = await session.execute(stmt)

    return result.scalars().first()
