"""
app/core/hs_config.py
---------------------
Quản lý danh sách HS Code mục tiêu.

Dữ liệu được lưu tại config/hs_codes.json (cùng cấp với thư mục backend).
Nếu file chưa tồn tại, module sẽ tự khởi tạo với danh sách mặc định.
"""

import json
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

# ── Hằng số đường dẫn ───────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(__file__)                          # backend/app/core
_ROOT_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))  # eagle_dataTool/
_CONFIG_DIR = os.path.join(_ROOT_DIR, "config")
_HS_JSON_PATH = os.path.join(_CONFIG_DIR, "hs_codes.json")

# ── Danh sách mặc định (chỉ dùng khi file chưa tồn tại) ────────────────────
_DEFAULT_HS_CODES: List[str] = [
    "3809", "3507", "3204", "3404",
    "3402", "3403", "3910", "3906",
    "2821", "3824",
]


# ── Helpers I/O ─────────────────────────────────────────────────────────────

def _ensure_config_dir() -> None:
    """Tạo thư mục config/ nếu chưa tồn tại."""
    os.makedirs(_CONFIG_DIR, exist_ok=True)


def _load_raw() -> List[str]:
    """Đọc raw list từ JSON. Trả về list rỗng nếu gặp lỗi."""
    if not os.path.exists(_HS_JSON_PATH):
        return []
    try:
        with open(_HS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(c).strip() for c in data if str(c).strip()]
    except Exception as exc:
        logger.error("Không đọc được hs_codes.json: %s", exc)
    return []


def _save_raw(codes: List[str]) -> None:
    """Ghi list về JSON (ghi đè)."""
    _ensure_config_dir()
    try:
        with open(_HS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(set(codes)), f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("Không ghi được hs_codes.json: %s", exc)
        raise


# ── Public API ───────────────────────────────────────────────────────────────

def get_hs_codes() -> List[str]:
    """
    Trả về danh sách HS Code hiện tại.
    Nếu file chưa tồn tại → khởi tạo với danh sách mặc định rồi trả về.
    """
    codes = _load_raw()
    if not codes:
        logger.info("hs_codes.json chưa tồn tại → khởi tạo danh sách mặc định.")
        _save_raw(_DEFAULT_HS_CODES)
        return list(_DEFAULT_HS_CODES)
    return codes


def add_hs_code(code: str) -> List[str]:
    """
    Thêm một HS Code mới.
    Raises ValueError nếu mã đã tồn tại.
    """
    code = code.strip()
    if not code:
        raise ValueError("HS Code không được để trống.")
    codes = get_hs_codes()
    if code in codes:
        raise ValueError(f"HS Code '{code}' đã tồn tại trong danh sách.")
    codes.append(code)
    _save_raw(codes)
    logger.info("Đã thêm HS Code: %s", code)
    return sorted(set(codes))


def remove_hs_code(code: str) -> List[str]:
    """
    Xóa một HS Code.
    Raises ValueError nếu mã không tồn tại.
    """
    code = code.strip()
    codes = get_hs_codes()
    if code not in codes:
        raise ValueError(f"HS Code '{code}' không tìm thấy trong danh sách.")
    codes = [c for c in codes if c != code]
    _save_raw(codes)
    logger.info("Đã xóa HS Code: %s", code)
    return sorted(set(codes))
