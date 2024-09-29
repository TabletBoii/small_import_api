import numpy as np
import pandas as pd

from sqlalchemy import create_engine
from utils.utils import get_data


field_names = {
    'partner$inc': 'ID партнера',
    'claim$cdatetime': 'Дата/время расчёта заявки',
    'claim$inc': 'Заявка №',
    'partner$name': 'Заказчик',
    'partner$state': 'Страна партнера',
    'partner$town$name': 'Город партнера',
    'supervisor$inc': 'Куратор ТА ID',
    'supervisor$name': 'Куратор ТА',
    'claim$datebeg': 'Дата начала тура',
    'claim$dateend': 'Дата окончания тура',
    'claim$nights': 'Ночей',
    'tour$name': 'Тур',
    'statefrom$name': 'Страна отправления',
    'state$name': 'Основная страна пребывания',
    'confimredstatus$name': 'Подтверждение',
    'ctype$name': 'Тип заявки',
    'adl_count': 'Взрослых',
    'chd_count': 'Детей',
    'all_pax': 'TOTAL PAX',
    'claim$total_commiss': 'Сумма комиссии',
    'commission$percent': 'Комиссия (%)',
    'claim$amount_to_pay': 'К оплате',
    'claim$currency$alias': '$',
    'claim$paidcost': 'Оплачено',
    'claim$debtcost': 'Долг',
    'claim$profit': 'Прибыль',
    'claim$paidstatus': 'Статус заявки',
    'claim$rdate': 'Дата/время создания заявки',
    'town$name': 'Город отправления',
    'departure$town$name': 'Город прибытия',
    'office$name': 'Офис',
    'pc$name': 'Категория партнера'
}

convert_timestamp_to_str_list = ['claim$cdatetime', 'claim$datebeg', 'claim$dateend', 'claim$rdate']


class ClaimsImport:
    def __init__(self, dates: tuple):
        self.dates = dates
        self.__imported_data = None
        self.KOMPAS_DB_SERVER = get_data("KOMPAS_DB_SERVER")
        self.KOMPAS_DB_USERNAME = get_data("KOMPAS_DB_USERNAME")
        self.KOMPAS_DB_PASSWORD = get_data("KOMPAS_DB_PASSWORD")
        self.KOMPAS_DB_NAME = get_data("KOMPAS_DB_NAME")
        self.connection_string = f"mssql+pytds://{self.KOMPAS_DB_USERNAME}:{self.KOMPAS_DB_PASSWORD}@{self.KOMPAS_DB_SERVER}:1433/{self.KOMPAS_DB_NAME}"
        self.__odbc_driver = "ODBC Driver 17 for SQL Server"
        self.columns = []

    def __execute_query(self, query: str):
        try:
            with create_engine(self.connection_string).connect() as db_conn:
                self.__imported_data = pd.read_sql(query, db_conn)
                selected_df = self.__imported_data.loc[:, list(field_names.keys())]
                selected_df = selected_df.where(pd.notnull(selected_df), None)
                selected_df = selected_df.replace(np.nan, None)
                selected_df = selected_df.rename(columns=field_names)
                data = selected_df.to_dict(orient='records')
                return data

        except Exception as e:
            raise e

    def __fetch_kompas_data(self):

        import_query = f"""
            SET NOCOUNT ON;
            EXEC	{get_data("PROCEDURE_NAME")}
            @cdate_from = N'{self.dates[0]}',
            @cdate_till = N'{self.dates[1]}'
        """
        return self.__execute_query(
            query=import_query
        )

    def run(self):
        return self.__fetch_kompas_data()
