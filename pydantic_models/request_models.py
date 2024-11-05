from pydantic import BaseModel
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
