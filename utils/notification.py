from datetime import datetime, timedelta
from sqlalchemy import select, update
from database.sessions import WEB_SESSION_FACTORY
from models.web.web_notification_model import WebNotificationModel


async def push_notify(uid: str, message: str, category: str = "info",
                      persist: bool = True, ttl_seconds: int | None = None):
    notif_id = None
    if persist:
        async with WEB_SESSION_FACTORY() as s:
            n = WebNotificationModel(
                user_id=uid, message=message, category=category,
                expires_at=(datetime.now() + timedelta(seconds=ttl_seconds)) if ttl_seconds else None
            )
            s.add(n)
            await s.commit()
            await s.refresh(n)
            notif_id = n.id
    # await manager.send(uid, {"id": notif_id, "message": message, "category": category})
