from fastapi import APIRouter

import os
from dotenv import load_dotenv

from utils.utils import get_api_key

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, UJSONResponse

from database.sessions import KOMPAS_SESSION_FACTORY

from callers.import_caller import get_agg_import_class, get_partner_directory_import_class
from controllers.agg_import import AggImport
from controllers.claims_import import ClaimsImport
from controllers.partner_directory_import import PartnerDirectoryImport

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)


@router.get("/import/", response_class=UJSONResponse)
async def import_claim_data(date_from: str, date_till: str):
    print(date_from, date_till)
    claims_import = ClaimsImport(dates=(date_from, date_till))
    imported_data = claims_import.run()
    json_compatible_data = jsonable_encoder(imported_data)
    # print(json_compatible_data)
    return JSONResponse(
        content=json_compatible_data,
        media_type="application/json; charset=utf-8"
    )


@router.get('/plan_import/', response_class=UJSONResponse)
async def import_plan_data(agg_import: AggImport = Depends(get_agg_import_class)):
    imported_data = await agg_import.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )


@router.get('/partner_directory/', response_class=UJSONResponse)
async def import_partner_directory(plan_directory: PartnerDirectoryImport = Depends(get_partner_directory_import_class)):
    plan_directory.set_session(session_factory=KOMPAS_SESSION_FACTORY)
    imported_data = await plan_directory.run()
    return JSONResponse(
        content=imported_data,
        media_type="application/json; charset=utf-8"
    )