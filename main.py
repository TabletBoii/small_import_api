from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery, APIKey
import os
from dotenv import load_dotenv

from callers.import_caller import get_agg_import, get_partner_directory_import
from middlewares.cancelled_middleware import RequestCancelledMiddleware
from utils.agg_import import AggImport
from utils.claims_import import ClaimsImport
from utils.partner_directory_import import PartnerDirectoryImport

app = FastAPI()
# app.add_middleware(RequestCancelledMiddleware)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(
    dotenv_path=dotenv_path
)

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"


api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header),
                      api_key_query: str = Security(api_key_query)) -> str:
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing API Key",
        )


@app.get("/check-api-key")
async def check_api_key(api_key: str = Depends(get_api_key)):
    return JSONResponse(
        content={
            "message": "OK"
        },
        status_code=200,
        media_type="application/json; charset=utf-8"
    )


@app.get("/import/", response_class=UJSONResponse)
async def import_claim_data(date_from: str, date_till: str, api_key: str = Depends(get_api_key)):
    print(date_from, date_till)
    claims_import = ClaimsImport(dates=(date_from, date_till))
    imported_data = claims_import.run()
    json_compatible_data = jsonable_encoder(imported_data)
    # print(json_compatible_data)
    return JSONResponse(
        content=json_compatible_data,
        media_type="application/json; charset=utf-8"
    )


@app.get('/plan_import/', response_class=UJSONResponse)
async def import_plan_data(year_from: str, state_inc: Optional[str] = None, agg_import: AggImport = Depends(get_agg_import), api_key: str = Depends(get_api_key)):
    imported_data = await agg_import.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )


@app.get('/partner_directory/', response_class=UJSONResponse)
async def import_partner_directory(state_inc: Optional[str] = None, plan_directory: PartnerDirectoryImport = Depends(get_partner_directory_import), api_key: str = Depends(get_api_key)):
    imported_data = await plan_directory.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )


@app.get("/public-data")
async def read_public_data():
    return {"message": "This is public data accessible without an API key"}
