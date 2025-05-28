from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Type, Optional

T = TypeVar('T')


class GenericResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, example=0)
    msg: str = Field(default="success", example="success")
    data: Optional[T]
