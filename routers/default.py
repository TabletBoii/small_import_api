from fastapi import APIRouter

from utils.utils import get_api_key

from fastapi import Depends
from fastapi.responses import JSONResponse

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)


@router.get("/check-api-key")
async def check_api_key():
    return JSONResponse(
        content={
            "message": "OK"
        },
        status_code=200,
        media_type="application/json; charset=utf-8"
    )
