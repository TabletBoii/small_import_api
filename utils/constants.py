import os

from fastapi.security import APIKeyHeader, APIKeyQuery

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access_token"

API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY_QUERY = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
