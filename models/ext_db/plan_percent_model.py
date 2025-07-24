from sqlalchemy import Column, Integer, Date, Float

from models.base import Base


class PlanPercentModel(Base):
    __tablename__ = "plan_percent_values"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    date = Column('date', Date)
    state = Column('state', Integer)
    percent = Column('state_percent', Float)
