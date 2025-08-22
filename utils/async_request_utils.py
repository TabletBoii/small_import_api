from typing import Optional, Any

import httpx
from httpx import AsyncClient


async def safe_json_get(client: AsyncClient, url: str) -> Optional[Any]:
    try:
        resp = await client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError:
        return None
