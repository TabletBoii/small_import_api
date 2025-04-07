import numpy as np
import pandas as pd
import operator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from pydantic_models.request_models import ClaimsBonusSystemModel
from utils.utils import process_result_data, find_min_date, find_max_date

ops = {
    "=": operator.eq,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "<>": operator.not_
}

custom_column_list = [
    "PaymentDateDiff", "PricePerPax"
]

class ClaimsBonusSystem:
    def __init__(self, condition_data: list[ClaimsBonusSystemModel]):
        self.session_factory: async_sessionmaker = None
        self.condition_data = condition_data

    def set_session(self, session_factory):
        self.session_factory = session_factory

    def generate_query(self, date_from, date_till):
        query = """
            SET NOCOUNT ON;
            EXEC [dbo].[up_claim_info_KOMPAS]
        """
        query += f" @cdate_from = N'{date_from}', @cdate_till = N'{date_till}'"

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
            if date_period["name"] != "claim$cdate" and len(condition_data.date_periods) > 1:
                date_name = date_period["name"]
                date_first_value = date_period["date_first"]
                date_last_value = date_period["date_last"]
                initial_df = initial_df[(initial_df[date_name] >= date_first_value) & (initial_df[date_name] <= date_last_value)]
        for condition in condition_data.conditions:
            uni_condition_name = condition["field_name"]
            uni_condition_sign = condition["sign"]
            uni_condition_value = condition["value"]
            uni_condition_value2 = condition["value2"]
            uni_condition_value_list = condition["value_list"]

            if uni_condition_sign in ops:
                op_func = ops[uni_condition_sign]
                initial_df = initial_df[op_func(initial_df[uni_condition_name], uni_condition_value)]
            elif uni_condition_sign == "Between":
                initial_df = initial_df[
                    (initial_df[uni_condition_name] >= uni_condition_value) &
                    (initial_df[uni_condition_name] <= uni_condition_value2)
                    ]
            elif uni_condition_sign == "In":
                if uni_condition_sign == "In":
                    initial_df = initial_df[initial_df[uni_condition_name].isin(uni_condition_value_list)]

        initial_df["Условия"] = condition_data.condition_name
        for unit in condition_data.conv_units:
            initial_df[unit["name"]] = unit["value"]
        return initial_df

    def get_query_date_periods(self):
        start_dates = []
        end_dates = []
        for condition in self.condition_data:
            for date_period in condition.date_periods:
                if date_period["name"] == "claim$cdate":
                    start_dates.append(date_period["date_first"])
                    end_dates.append(date_period["date_last"])
                elif date_period["name"] != "claim$cdate" and len(condition.date_periods) == 1:
                    start_dates.append(date_period["date_first"])
                    end_dates.append(date_period["date_last"])
        return find_min_date(start_dates), find_max_date(end_dates)

    async def run(self):
        # TODO: добавить условие, при котором выбирается поле datebeg если claim_date нет
        date_from, date_till = self.get_query_date_periods()
        print(self.condition_data)
        claim_list_by_claim_date_query = self.generate_query(date_from, date_till)
        print("Query generated")
        print(claim_list_by_claim_date_query)
        claim_list_by_claim_date = await self.__execute_query(claim_list_by_claim_date_query)
        print("Query proceeded")
        df_list = []
        await self.add_custom_columns(claim_list_by_claim_date)
        for condition in self.condition_data:
            df_cond = await self.apply_conditions(claim_list_by_claim_date, condition)
            df_list.append(df_cond)

        combined_df = pd.concat(df_list, ignore_index=True)

        combined_df = process_result_data(combined_df)
        print("transformation finished")
        return combined_df
