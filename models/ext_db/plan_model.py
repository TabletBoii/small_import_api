from sqlalchemy import Column, Integer, String, Boolean

from models.models import Base


class PlanModel(Base):
    __tablename__ = "plan_data"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    partner_inc = Column('partner_inc', Integer)
    partner_town_name = Column('partner_town_name', String)
    partner_name = Column('partner_name', String)
    partner_category_name = Column('partner_category_name', String)
    partner_add_date = Column('partner_add_date', String)
    partner_internet = Column('partner_internet', Boolean)
    supervisor_name = Column('supervisor_name', String)
    partner_parttype_name = Column('partner_parttype_name', String)
    plan_value = Column('plan_value', Integer)
