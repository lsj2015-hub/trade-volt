from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class MarketType(str, enum.Enum):
    KOR = "KOR"
    OVERSEAS = "OVERSEAS"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String, index=True, nullable=False)
    stock_name = Column(String, nullable=False)
    market = Column(SQLAlchemyEnum(MarketType), nullable=False)
    transaction_type = Column(SQLAlchemyEnum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)