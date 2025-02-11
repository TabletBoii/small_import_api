import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder
from pandas import DataFrame
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import UpdateObOpModel
from datetime import datetime

from utils.utils import convert_iso_string_to_datetime, get_data
import pytz

field_names = {
    'state$name': 'Основная страна пребывания',
    'claim$inc': 'Заявка №',
    'partner$name': 'Заказчик',
    'claim$privatecomment': 'Внутреннее примечание',
    'partner$town$name': 'Город',
    'tilldate$begin': 'Дней до начала тура',
    'partner$phone': 'Контактное лицо',
    'claim$datebeg': 'Дата начала тура',
    'claim$confirmeddate': 'Дата подтверждения/неподтверждения',
    'confimredstatus$name': 'Статус'
}


class ClaimsInBetweenUploader:
    def __init__(self, last_claim_data: list[UpdateObOpModel]):
        self.session_factory: async_sessionmaker = None
        self.last_claim_conf_date = last_claim_data[0].last_claim_conf_date

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def get_formated_query(self, date_from: str, date_till: str) -> str:
        import_query = f"""
            SET NOCOUNT ON;
            EXEC	{get_data("CUSTOM_PROCEDURE_NAME")}
            @confirmeddate_from = N'{date_from}',
            @confirmeddate_till = N'{date_till}',
		    @confirmedstatus_value = 1,
		    @paidstatus_value = 1
        """
        return import_query

    async def __execute_query(self, query: str):
        try:
            async with self.session_factory() as session:
                result = await session.execute(text(query))
        except Exception as e:
            # print(e)
            raise e
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        return df

    def get_ongoing_claim_data(self):
        pass

    def process_result_data(self, fetched_data: DataFrame):
        fetched_data = fetched_data.loc[:, list(field_names.keys())]
        fetched_data = fetched_data.replace(np.nan, None)
        fetched_data = fetched_data.rename(columns=field_names)
        fetched_data = fetched_data.to_dict(orient='records')
        resulted_data = jsonable_encoder(fetched_data)
        return resulted_data

    async def run(self):
        if self.last_claim_conf_date is None:
            pass
        # self.last_claim_conf_date = "2025-01-26T10:33:00.000Z"
        self.last_claim_conf_date = convert_iso_string_to_datetime(self.last_claim_conf_date)
        formated_from_date = self.last_claim_conf_date.strftime("%Y-%m-%d %H:%M")

        timezone = pytz.timezone("Asia/Karachi")

        formated_till_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M")
        unconfirmed_claims_query = self.get_formated_query(formated_from_date, formated_till_date)
        fetched_data = await self.__execute_query(unconfirmed_claims_query)
        return self.process_result_data(fetched_data)
