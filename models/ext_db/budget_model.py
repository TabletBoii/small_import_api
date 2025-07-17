from sqlalchemy import Column, Integer, String, Unicode, Float

from models.models import Base


class BudgetModel(Base):
    __tablename__ = "budget_data"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    department = Column('department', String)
    date = Column('date', String)
    manager = Column('manager', Unicode(200))
    state = Column('state', String)
    markdep = Column('markdep', String)
    standard_days = Column('standard_days', Integer)
    worked_fact = Column('worked_fact', Integer)
    overtime_days = Column('overtime_days', Integer)
    net_with_taxes = Column('net_with_taxes', Float)
    overtime_with_taxes = Column('overtime_with_taxes', Float)
    bonus_with_taxes = Column('bonus_with_taxes', Float)
    total_with_taxes = Column('total_with_taxes', Float)
    net_in_hands = Column('net_in_hands', Float)
    overtime_in_hands = Column('overtime_in_hands', Float)
    bonus_in_hands = Column('bonus_in_hands', Float)
    total_in_hands = Column('total_in_hands', Float)
