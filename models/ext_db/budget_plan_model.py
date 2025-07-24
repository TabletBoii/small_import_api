from sqlalchemy import Column, Integer, String

from models.base import Base


class BudgetPlanModel(Base):
    __tablename__ = "budget_plan_data"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    manager = Column('manager', String)
    job_title = Column('job_title', String)
    currency = Column('currency', String)
    salary_hand = Column('salary_hand', Integer)
    oper_kpi = Column('oper_kpi', Integer)
    finance_kpi = Column('finance_kpi', Integer)
    total_salary = Column('total_salary', Integer)
