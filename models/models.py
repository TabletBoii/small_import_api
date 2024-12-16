from sqlalchemy import String, Column, Integer, UniqueConstraint, TIMESTAMP, DOUBLE_PRECISION, DateTime, Boolean, Float, \
    Date, Unicode
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PlanData(Base):
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


class BudgetData(Base):
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


class BudgetCurrencyData(Base):
    __tablename__ = "budget_currency"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    date = Column('date', Date)
    currency = Column('currency', String)
    value = Column('value', Float)


class BudgetPlanData(Base):
    __tablename__ = "budget_plan_data"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    manager = Column('manager', String)
    job_title = Column('job_title', String)
    currency = Column('currency', String)
    salary_hand = Column('salary_hand', Integer)
    oper_kpi = Column('oper_kpi', Integer)
    finance_kpi = Column('finance_kpi', Integer)
    total_salary = Column('total_salary', Integer)
