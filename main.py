from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery, APIKey
import os
from dotenv import load_dotenv

from utils.agg_import import AggImport
from utils.claims_import import ClaimsImport

app = FastAPI()

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
async def import_plan_data(year_from: str, api_key: str = Depends(get_api_key)):
    aggregated_import = AggImport(year_from=year_from)
    imported_data = await aggregated_import.run()
    json_compatible_data = jsonable_encoder(imported_data)
    return JSONResponse(
        content=json_compatible_data,
        media_type="application/json; charset=utf-8"
    )


@app.get("/public-data")
async def read_public_data():
    return {"message": "This is public data accessible without an API key"}