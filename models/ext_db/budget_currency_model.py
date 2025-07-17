from sqlalchemy import Column, Integer, Date, String, Float

from models.models import Base


class BudgetCurrencyModel(Base):
    __tablename__ = "budget_currency"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    date = Column('date', Date)
    currency = Column('currency', String)
    value = Column('value', Float)
