from typing import Optional, Dict, List

from pydantic import BaseModel, RootModel
import datetime


class PlanValuesModel(BaseModel):
    partner_inc: int
    partner_town_name: str
    partner_name: str
    partner_category_name: str | None = None
    partner_add_date: str
    partner_internet: bool
    supervisor_name: str | None = None
    partner_parttype_name: str | None = None
    plan_value: int | None = 0

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, orm_model):
        return cls.from_orm(orm_model)


class BudgetValuesModel(BaseModel):
    department: str
    date: str
    manager: str
    state: str
    markdep: str
    standard_days: int
    worked_fact: int
    overtime_days: int
    net_with_taxes: Optional[float]
    overtime_with_taxes: Optional[float]
    bonus_with_taxes: Optional[float]
    total_with_taxes: Optional[float]
    net_in_hands: Optional[float]
    overtime_in_hands: Optional[float]
    bonus_in_hands: Optional[float]
    total_in_hands: Optional[float]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, orm_model):
        return cls.from_orm(orm_model)


class BudgetCurrencyModel(BaseModel):
    date: str
    currency: str
    value: int

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, orm_model):
        return cls.from_orm(orm_model)
