import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import ClaimsBonusSystemModel


class ClaimsBonusSystem:
    def __init__(self, condition_data: list[ClaimsBonusSystemModel]):
        self.session_factory: async_sessionmaker = None
        self.condition_data = condition_data

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def generate_query(self, date_periods):
        query = """
            EXEC [dbo].[up_claim_info_KOMPAS]
        """
        for date_period in date_periods:
            if date_period["name"] == "claim_date":
                query += f" @cdate_from = N'{date_period["date_first"]}', @cdate_till = N'{[date_period["date_last"]]}'"

        return query

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

    async def apply_conditions(self, initial_df, condition_data: ClaimsBonusSystemModel):
        for date_period in condition_data.date_periods:
            if date_period["name"] != "claim$cdate":
                date_name = date_period["name"]
                date_first_value = date_period["date_first"]
                date_last_value = date_period["date_last"]
                initial_df = initial_df[(initial_df[date_name] >= date_first_value) & (initial_df[date_name] <= date_last_value)]
        for condition in condition_data.conditions:
            uni_condition_name = condition["field_name"]
            uni_condition_sign = condition["sign"]
            uni_condition_value = condition["value"]
            uni_condition_value_list = condition["value_list"]
            if uni_condition_sign == "=":
                initial_df = initial_df[initial_df[uni_condition_name] == uni_condition_value]
            elif uni_condition_sign == ">":
                initial_df = initial_df[initial_df[uni_condition_name] > uni_condition_value]
            elif uni_condition_sign == ">=":
                initial_df = initial_df[initial_df[uni_condition_name] >= uni_condition_value]
            elif uni_condition_sign == "<":
                initial_df = initial_df[initial_df[uni_condition_name] < uni_condition_value]
            elif uni_condition_sign == "<=":
                initial_df = initial_df[initial_df[uni_condition_name] <= uni_condition_value]
        initial_df["Условия"] = condition_data.condition_name
        for unit in condition_data.conv_units:
            initial_df[unit["name"]] = unit["value"]
        return initial_df

    async def run(self):
        print(self.condition_data)
        filter_date_periods = self.condition_data[0].date_periods
        claim_list_by_claim_date_query = self.generate_query(filter_date_periods)
        claim_list_by_claim_date = await self.__execute_query(claim_list_by_claim_date_query)
        transformed_df = await self.apply_conditions(claim_list_by_claim_date, self.condition_data[0])
        return transformed_df