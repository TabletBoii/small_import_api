from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import UpdateObOpModel
from datetime import datetime

from utils.utils import convert_iso_string_to_datetime, get_data


class ClaimsInBetweenUploader:
    def __init__(self, last_claim_data: UpdateObOpModel):
        self.session_factory: async_sessionmaker = None
        self.last_claim_conf_date = last_claim_data.last_claim_conf_date

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def get_formated_query(self, date_from: str, date_till: str) -> str:
        import_query = f"""
            SET NOCOUNT ON;
            EXEC	{get_data("PLAN_PROCEDURE_NAME")}
            @confirmeddate_from = N'{date_from}',
            @confirmeddate_till = N'{date_till}',
        """
        return import_query

    def get_ongoing_claim_data(self):
        pass

    async def run(self):
        if self.last_claim_conf_date is None:
            pass
        self.last_claim_conf_date = "2025-01-26T10:33:00.000Z"
        self.last_claim_conf_date = convert_iso_string_to_datetime(self.last_claim_conf_date)
        # 20230101
        formated_date = self.last_claim_conf_date.strftime("")
        # print(converted_datetime)
        current_date = datetime.now()

        print(self.last_claim_conf_date)
