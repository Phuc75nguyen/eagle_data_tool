from datetime import datetime
import logging
from app.models.trade_record import TradeRecord

logger = logging.getLogger(__name__)

def normalize_data(raw_item: dict) -> TradeRecord:
    """
    Chuẩn hóa 11 cột Excel/JSON sang TradeRecord Database Model.
    """
    try:
        date_str = str(raw_item.get("Date", "") or "").split("T")[0]
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
    except Exception:
        parsed_date = None

    return TradeRecord(
        date=parsed_date,
        importer=str(raw_item.get("Importer", "") or raw_item.get("importer", "")),
        hs_code=str(raw_item.get("HsCode", "") or raw_item.get("hsCode", "")),
        product=str(raw_item.get("Product", "") or raw_item.get("product", "")),
        quantity=float(raw_item.get("Quantity") or raw_item.get("quantity") or 0.0),
        quantity_unit=str(raw_item.get("QuantityUnit", "") or raw_item.get("quantityUnit", "")),
        value=float(raw_item.get("Value") or raw_item.get("value") or 0.0),
        value_unit=str(raw_item.get("ValueUnit", "") or raw_item.get("valueUnit", "")),
        unit_price=float(raw_item.get("UnitPrice") or raw_item.get("unitPrice") or 0.0)
    )
