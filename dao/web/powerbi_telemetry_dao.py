from sqlalchemy.ext.asyncio import AsyncSession

from models.web.web_pbi_telemetry_model import WebPbiTelemetryModel


async def create(session: AsyncSession, telemetry_instance: WebPbiTelemetryModel):
    session.add(telemetry_instance)
    await session.commit()
