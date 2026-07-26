"""
app/services/processor_service.py
----------------------------------
Chịu trách nhiệm:
  1. strict_hscode_filter() — lọc gắt record theo danh sách HS Code mục tiêu.
  2. normalize_data()       — chuẩn hóa dict thô → TradeRecord ORM object (11 cột).
"""

import logging
import re
from datetime import datetime
from typing import List, Dict

from app.models.trade_record import TradeRecord

logger = logging.getLogger(__name__)

# Dữ liệu thô từ TradeData có dạng: "<CODE>#&AMP;<Mô tả tiếng Anh>;<CODE>#&<Mô tả tiếng Việt>"
# Ta chỉ giữ lại phần mô tả tiếng Anh đầu tiên và bỏ mã kỹ thuật ở đầu.
_PRODUCT_CODE_PREFIX_RE = re.compile(r"^[\w\-.]+#&(?:AMP;)?\s*", re.IGNORECASE)


# ── Helper ───────────────────────────────────────────────────────────────────

def _safe_float(value) -> float:
    """Chuyển giá trị sang float an toàn; trả 0.0 nếu lỗi."""
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _safe_str(*candidates) -> str:
    """Trả về chuỗi không rỗng đầu tiên từ danh sách ứng viên."""
    for c in candidates:
        if c is not None and str(c).strip():
            return str(c).strip()
    return ""


def _parse_date(raw: str):
    """Parse YYYY-MM-DD (cắt bỏ phần giờ nếu có). Trả None nếu lỗi."""
    if not raw:
        return None
    try:
        date_str = str(raw).split("T")[0].strip()
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None


def clean_product_name(raw: str) -> str:
    """
    Làm sạch cột Product theo yêu cầu khách hàng:
      - Bỏ phần mô tả tiếng Việt trùng lặp đứng sau dấu ';'.
      - Bỏ mã kỹ thuật + ký tự nhiễu dạng "CODE#&AMP;" / "CODE#&" ở đầu chuỗi.
    """
    if not raw:
        return ""
    # Bỏ mã kỹ thuật trước — bên trong nó có dấu ';' (vd "AMP;") nên phải xử lý
    # trước khi split theo ';', nếu không sẽ cắt nhầm ngay giữa mã.
    text = _PRODUCT_CODE_PREFIX_RE.sub("", str(raw).strip()).strip()
    text = text.split(";")[0].strip()
    return text


# ── Public: Strict HS Code Filter ────────────────────────────────────────────

def strict_hscode_filter(
    raw_records: List[Dict],
    target_hscodes: List[str],
) -> List[Dict]:
    """
    Lọc gắt danh sách record thô.

    Chỉ giữ lại các record mà trường HsCode bắt đầu bằng (startswith)
    ít nhất một mã trong ``target_hscodes``.

    Args:
        raw_records:     Danh sách dict thô lấy thẳng từ API TradeData.
        target_hscodes:  Danh sách prefix HS Code cần giữ (ví dụ ["3809", "3402"]).

    Returns:
        Danh sách dict đã lọc.
    """
    if not target_hscodes:
        logger.warning("target_hscodes rỗng → bỏ qua filter, trả về toàn bộ record.")
        return raw_records

    kept: List[Dict] = []
    dropped = 0

    for record in raw_records:
        # Thử lấy HsCode từ nhiều key khác nhau (API có thể trả về camelCase hoặc PascalCase)
        hs_raw = _safe_str(
            record.get("HsCode"),
            record.get("hsCode"),
            record.get("hs_code"),
        )

        matched = any(hs_raw.startswith(prefix) for prefix in target_hscodes)
        if matched:
            kept.append(record)
        else:
            dropped += 1

    logger.info(
        "strict_hscode_filter: giữ lại %d / %d record (đã drop %d record rác).",
        len(kept), len(raw_records), dropped,
    )
    return kept


# ── Public: Normalize to ORM ──────────────────────────────────────────────────

def normalize_data(raw_item: Dict) -> TradeRecord:
    """
    Chuẩn hóa một dict thô từ API thành TradeRecord ORM (11 cột chuẩn).

    Mapping các key theo cả PascalCase (API trả về) và snake_case:
        date, origin_country, exporter, importer, hs_code, product,
        quantity, quantity_unit, value, value_unit, unit_price
    """
    return TradeRecord(
        date=_parse_date(
            _safe_str(raw_item.get("Date"), raw_item.get("date"))
        ),
        origin_country=_safe_str(
            raw_item.get("OriginCountry"),
            raw_item.get("originCountry"),
            raw_item.get("origin_country"),
            raw_item.get("Country"),
            raw_item.get("country"),
        ),
        exporter=_safe_str(
            raw_item.get("Exporter"),
            raw_item.get("exporter"),
        ),
        importer=_safe_str(
            raw_item.get("Importer"),
            raw_item.get("importer"),
        ),
        hs_code=_safe_str(
            raw_item.get("HsCode"),
            raw_item.get("hsCode"),
            raw_item.get("hs_code"),
        ),
        product=clean_product_name(
            _safe_str(raw_item.get("Product"), raw_item.get("product"))
        ),
        quantity=(quantity := _safe_float(
            raw_item.get("Quantity") or raw_item.get("quantity")
        )),
        quantity_unit=_safe_str(
            raw_item.get("QuantityUnit"),
            raw_item.get("quantityUnit"),
            raw_item.get("quantity_unit"),
        ),
        value=(value := _safe_float(
            raw_item.get("Value") or raw_item.get("value")
        )),
        value_unit=_safe_str(
            raw_item.get("ValueUnit"),
            raw_item.get("valueUnit"),
            raw_item.get("value_unit"),
        ),
        # Unit Price = Value / Quantity, làm tròn 2 chữ số thập phân (theo yêu cầu khách hàng).
        unit_price=round(value / quantity, 2) if quantity else 0.0,
    )
