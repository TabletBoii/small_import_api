from typing import Self, Optional

from pydantic import BaseModel


class EditAdminUser(BaseModel):
    name: str
    microsoft_email: Optional[str]
    microsoft_oid: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, orm_model) -> Self:
        return cls.from_orm(orm_model)
