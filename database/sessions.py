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
WEB_DB_NAME = get_data("WEB_DB_NAME")

WEB_DEV_DB_SERVER = get_data("WEB_DEV_DB_SERVER")
WEB_DEV_DB_USERNAME = get_data("WEB_DEV_DB_USERNAME")
WEB_DEV_DB_PASSWORD = get_data("WEB_DEV_DB_PASSWORD")
WEB_DEV_DB_NAME = get_data("WEB_DEV_DB_NAME")

PG_ODBC_SERVER = "PostgreSQL+Unicode(x64)"


samotour_db_connection_string = f"mssql+aioodbc://{KOMPAS_DB_USERNAME}:{KOMPAS_DB_PASSWORD}@{KOMPAS_DB_SERVER}:1433/{KOMPAS_DB_NAME}?driver={ODBC_DRIVER}"
plan_db_connection_string = f"mssql+aioodbc://{PLAN_DB_USERNAME}:{PLAN_DB_PASSWORD}@{PLAN_DB_SERVER}:1433/{PLAN_DB_NAME}?driver={ODBC_DRIVER}"
dev_web_db_connection_string = f"postgresql+asyncpg://{WEB_DEV_DB_USERNAME}:{WEB_DEV_DB_PASSWORD}@{WEB_DEV_DB_SERVER}:5433/{WEB_DEV_DB_NAME}"

web_db_connection_string = f"mssql+aioodbc://{PLAN_DB_USERNAME}:{PLAN_DB_PASSWORD}@{PLAN_DB_SERVER}:1433/{WEB_DB_NAME}?driver={ODBC_DRIVER}"

KOMPAS_ENGINE = create_async_engine(
    samotour_db_connection_string,
    pool_size=10,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
)
PLAN_ENGINE = create_async_engine(
    plan_db_connection_string,
    pool_size=10,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
)
WEB_DEV_ENGINE = create_async_engine(
    dev_web_db_connection_string,
    pool_size=10,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
)
WEB_ENGINE = create_async_engine(
    web_db_connection_string,
    pool_size=10,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
)

KOMPAS_SESSION_FACTORY = async_sessionmaker(bind=KOMPAS_ENGINE, expire_on_commit=False)
PLAN_SESSION_FACTORY = async_sessionmaker(bind=PLAN_ENGINE, expire_on_commit=False)
WEB_DEV_SESSION_FACTORY = async_sessionmaker(bind=WEB_DEV_ENGINE, expire_on_commit=False)
WEB_SESSION_FACTORY = async_sessionmaker(bind=WEB_ENGINE, expire_on_commit=False)
