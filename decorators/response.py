import functools
import logging
from fastapi import HTTPException, status
from typing import Optional, Any
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[int] = None


def unified_response(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            if isinstance(result, dict):
                return APIResponse(success=True, message="OK", data=result)
            elif isinstance(result, APIResponse):
                return result
            else:
                return APIResponse(success=True, message="OK", data=result)
        except HTTPException as http_exc:
            return APIResponse(
                success=False,
                message=http_exc.detail,
                error_code=http_exc.status_code
            )
        except Exception as e:
            logging.exception("An unexpected error occurred.")
            return APIResponse(
                success=False,
                message=str(e),
                error_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper
