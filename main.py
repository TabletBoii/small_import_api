import sys
from typing import Optional

import os
from dotenv import load_dotenv

from controllers.upload_budget import UploadBudgetData
from controllers.upload_budget_curreny_data import UploadBudgetCurrencyData

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(
    dotenv_path=dotenv_path
)

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

from controllers.upload_plan import UploadPlanData
from database.sessions import KOMPAS_ENGINE, PLAN_ENGINE, KOMPAS_SESSION_FACTORY, PLAN_SESSION_FACTORY

from callers.import_caller import get_agg_import_class, get_partner_directory_import_class, get_upload_plan_class, \
    get_upload_budget_class, get_upload_budget_currency_class
from controllers.agg_import import AggImport
from controllers.claims_import import ClaimsImport
from controllers.partner_directory_import import PartnerDirectoryImport


sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI()
# app.add_middleware(RequestCancelledMiddleware)


API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


@app.on_event("shutdown")
async def shutdown_event():
    print("Application closes")
    await KOMPAS_ENGINE.dispose()
    await PLAN_ENGINE.dispose()


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
async def import_plan_data(agg_import: AggImport = Depends(get_agg_import_class), api_key: str = Depends(get_api_key)):
    imported_data = await agg_import.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )


@app.get('/partner_directory/', response_class=UJSONResponse)
async def import_partner_directory(plan_directory: PartnerDirectoryImport = Depends(get_partner_directory_import_class),
                                   api_key: str = Depends(get_api_key)):
    plan_directory.set_session(session_factory=KOMPAS_SESSION_FACTORY)
    imported_data = await plan_directory.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )


@app.post('/upload_plan_values')
async def upload_plan_values(upload_plan: UploadPlanData = Depends(get_upload_plan_class),
                             api_key: str = Depends(get_api_key)):
    upload_plan.set_session(session_factory=PLAN_SESSION_FACTORY)
    await upload_plan.run()
    return "Uploaded"


@app.post('/upload_budget_values')
async def upload_plan_values(upload_budget: UploadBudgetData = Depends(get_upload_budget_class),
                             api_key: str = Depends(get_api_key)):
    upload_budget.set_session(session_factory=PLAN_SESSION_FACTORY)
    await upload_budget.run()
    return "Uploaded"


@app.post('/upload_budget_currency')
async def upload_budget_currency_values(upload_budget_currency: UploadBudgetCurrencyData = Depends(get_upload_budget_currency_class),
                                        api_key: str = Depends(get_api_key)):
    upload_budget_currency.set_session(session_factory=PLAN_SESSION_FACTORY)
    await upload_budget_currency.run()
    return "Uploaded"


@app.get("/public-data")
async def read_public_data():
    return {"message": "This is public data accessible without an API key"}
