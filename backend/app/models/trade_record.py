from sqlalchemy import Column, Integer, String, Float, Date
from app.core.database import Base


class TradeRecord(Base):
    """
    Bảng CSDL cho dữ liệu Xuất-Nhập khẩu.
    Đủ 11 cột theo chuẩn EaglePax:
        date, origin_country, exporter, importer, hs_code, product,
        quantity, quantity_unit, value, value_unit, unit_price
    """
    __tablename__ = "trade_records"

    id             = Column(Integer, primary_key=True, index=True)
    date           = Column(Date,   index=True)
    origin_country = Column(String, index=True, default="")
    exporter       = Column(String, index=True, default="")
    importer       = Column(String, index=True, default="")
    hs_code        = Column(String, index=True, default="")
    product        = Column(String, index=True, default="")
    quantity       = Column(Float,  default=0.0)
    quantity_unit  = Column(String, default="")
    value          = Column(Float,  default=0.0)
    value_unit     = Column(String, default="")
    unit_price     = Column(Float,  default=0.0)
