from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base

class TradeRecord(Base):
    __tablename__ = "trade_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    importer = Column(String, index=True)
    hs_code = Column(String, index=True)
    product = Column(String, index=True)
    quantity = Column(Float)
    quantity_unit = Column(String)
    value = Column(Float)
    value_unit = Column(String)
    unit_price = Column(Float)
