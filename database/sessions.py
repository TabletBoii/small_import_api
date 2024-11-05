from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from utils.utils import get_data

ODBC_DRIVER = "ODBC Driver 17 for SQL Server"
KOMPAS_DB_SERVER = get_data("KOMPAS_DB_SERVER")
KOMPAS_DB_USERNAME = get_data("KOMPAS_DB_USERNAME")
KOMPAS_DB_PASSWORD = get_data("KOMPAS_DB_PASSWORD")
KOMPAS_DB_NAME = get_data("KOMPAS_DB_NAME")

PLAN_DB_SERVER = get_data("PLAN_DB_SERVER")
PLAN_DB_USERNAME = get_data("PLAN_DB_USERNAME")
PLAN_DB_PASSWORD = get_data("PLAN_DB_PASSWORD")
PLAN_DB_NAME = get_data("PLAN_DB_NAME")


samotour_db_connection_string = f"mssql+aioodbc://{KOMPAS_DB_USERNAME}:{KOMPAS_DB_PASSWORD}@{KOMPAS_DB_SERVER}:1433/{KOMPAS_DB_NAME}?driver={ODBC_DRIVER}"
plan_db_connection_string = f"mssql+aioodbc://{PLAN_DB_USERNAME}:{PLAN_DB_PASSWORD}@{PLAN_DB_SERVER}:1433/{PLAN_DB_NAME}?driver={ODBC_DRIVER}"

KOMPAS_ENGINE = create_async_engine(samotour_db_connection_string, pool_size=10, max_overflow=0)
PLAN_ENGINE = create_async_engine(plan_db_connection_string, pool_size=10, max_overflow=0)

KOMPAS_SESSION = async_sessionmaker(bind=KOMPAS_ENGINE, expire_on_commit=False)
PLAN_SESSION = async_sessionmaker(bind=PLAN_ENGINE, expire_on_commit=False)
