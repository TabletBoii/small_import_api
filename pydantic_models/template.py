from pydantic import BaseModel
from typing import List


class TemplateBase(BaseModel):
    report_key: str
    name: str


class TemplateCreate(TemplateBase):
    fields: List[str]


class TemplateResponse(TemplateBase):
    id: int

    class Config:
        orm_mode = True
