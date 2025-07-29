from typing import Any

from fastapi import Depends
from starlette.requests import Request

from routers.web_router.utils import make_route_permission_deps
from routers.web_router.web import web_jinja_router, templates
from utils.utils import require_user
import os, time, requests
from msal import ConfidentialClientApplication

TENANT_ID = os.getenv("ENTRA_TENANT_ID")
CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ENTRA_CLIENT_SECRET")
WORKSPACE_ID = os.getenv("PBI_WORKSPACE_ID")
REPORT_ID = os.getenv("PBI_REPORT_ID")

app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET
)


def get_pbi_access_token():
    result = app.acquire_token_for_client(
        scopes=["https://analysis.windows.net/powerbi/api/.default"]
    )
    if "access_token" not in result:
        raise ValueError("Could not acquire PBI access token: " + str(result))
    return result["access_token"]


def get_embed_params():
    access_token = get_pbi_access_token()

    resp = requests.get(
        f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    resp.raise_for_status()
    report = resp.json()

    token_resp = requests.post(
        f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"accessLevel": "View"}
    )
    token_resp.raise_for_status()
    embed_info = token_resp.json()

    return {
        "embedUrl": report["embedUrl"],
        "embedToken": embed_info["token"],
        "expiration": embed_info["expiration"]
    }


@web_jinja_router.get("/power_bi_base/embed-params")
def embed_params():
    return get_embed_params()


@web_jinja_router.get("/power_bi_base/{report_name}")
async def power_bi_base(
        request: Request,
        report_name: str,
        user: str = Depends(require_user),
        _perm: Any = Depends(make_route_permission_deps)
):
    return templates.TemplateResponse(
        "power_bi_base.html",
        {
            "request": request,
            "user": user,
            "data": report_name,
            "error": None,
        }
    )
