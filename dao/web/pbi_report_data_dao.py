from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dao.web.resource_dao import get_web_resource_by_name
from models.web.web_pbi_report_data_model import WebPbiReportDataModel
from models.web.web_resource_model import WebResourceModel


async def get_pbi_report_data_by_resource_id(session: AsyncSession, resource_id: int) -> WebPbiReportDataModel:
    stmt = (
        select(WebPbiReportDataModel).where(WebPbiReportDataModel.resource_id == resource_id)
    )

    result = await session.execute(stmt)

    return result.scalars().first()


async def get_pbi_report_data_by_resource_name(
    session: AsyncSession, resource_name: str
) -> WebPbiReportDataModel | None:
    stmt = (
        select(WebPbiReportDataModel)
        .join(WebResourceModel, WebResourceModel.inc == WebPbiReportDataModel.resource_id)
        .where(WebResourceModel.name == resource_name)
        .limit(1)
    )
    return await session.scalar(stmt)
