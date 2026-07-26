"""
app/core/company_config.py
---------------------------
Quản lý danh sách công ty mục tiêu (kèm HS Code tương ứng) dùng để crawl.

Người dùng upload file Excel (vd "TEXTILE COMPANY.xlsx") từ giao diện,
KHÔNG hard-code tên công ty vào mã nguồn (theo yêu cầu khách hàng).

Dữ liệu được lưu tại config/companies.json:
    [{"company_name": "...", "hs_code": "3809"}, ...]
"""

import json
import logging
import os
from io import BytesIO
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

# ── Hằng số đường dẫn ───────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(__file__)                                   # backend/app/core
_ROOT_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))  # eagle_dataTool/
_CONFIG_DIR = os.path.join(_ROOT_DIR, "config")
_COMPANIES_JSON_PATH = os.path.join(_CONFIG_DIR, "companies.json")


# ── Helpers I/O ─────────────────────────────────────────────────────────────

def _ensure_config_dir() -> None:
    os.makedirs(_CONFIG_DIR, exist_ok=True)


def _load_raw() -> List[Dict]:
    if not os.path.exists(_COMPANIES_JSON_PATH):
        return []
    try:
        with open(_COMPANIES_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as exc:
        logger.error("Không đọc được companies.json: %s", exc)
    return []


def _save_raw(companies: List[Dict]) -> None:
    _ensure_config_dir()
    try:
        with open(_COMPANIES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("Không ghi được companies.json: %s", exc)
        raise


# ── Public API ───────────────────────────────────────────────────────────────

def get_companies() -> List[Dict]:
    """Trả về danh sách công ty mục tiêu hiện tại (rỗng nếu chưa upload file nào)."""
    return _load_raw()


def get_company_names() -> List[str]:
    """Trả về danh sách tên công ty (bỏ qua HS Code), dùng để build filter cho crawler."""
    return [c["company_name"] for c in get_companies() if c.get("company_name")]


def _find_header_row(raw_df: pd.DataFrame) -> int:
    """
    File mẫu khách hàng có thể có 1 dòng tiêu đề phụ phía trên dòng header thật
    (vd dòng 0 chỉ có chữ "SERACH", dòng 1 mới thực sự là "NO"/"COMPANY NAME"/"HS CODE").

    Dò dòng đầu tiên chứa cả "COMPANY" và "NAME" để xác định header thật.
    Nếu không tìm thấy, giả định dòng đầu tiên (index 0) là header.
    """
    for idx, row in raw_df.iterrows():
        joined = " ".join(str(c).strip().upper() for c in row.tolist())
        if "COMPANY" in joined and "NAME" in joined:
            return idx
    return 0


def parse_company_excel(file_bytes: bytes) -> List[Dict]:
    """
    Parse file Excel danh sách công ty do người dùng upload.

    Tự động dò dòng header thật, tìm cột tên công ty (chứa "COMPANY"+"NAME")
    và cột HS Code (chứa "HS"), bỏ qua các dòng trống/không hợp lệ.

    Raises ValueError nếu không tìm thấy đủ cột cần thiết hoặc không có dữ liệu.
    """
    header_probe = pd.read_excel(BytesIO(file_bytes), header=None)
    header_idx = _find_header_row(header_probe)

    df = pd.read_excel(BytesIO(file_bytes), header=header_idx)
    df.columns = [str(c).strip().upper() for c in df.columns]

    company_col = next((c for c in df.columns if "COMPANY" in c and "NAME" in c), None)
    hscode_col = next((c for c in df.columns if "HS" in c), None)

    if not company_col:
        raise ValueError("Không tìm thấy cột tên công ty (COMPANY NAME) trong file.")
    if not hscode_col:
        raise ValueError("Không tìm thấy cột HS Code trong file.")

    companies: List[Dict] = []
    for _, row in df.iterrows():
        name = str(row.get(company_col, "")).strip()
        if not name or name.upper() == "NAN":
            continue

        # HS Code là thông tin THAM KHẢO, không bắt buộc — thực tế đa số công ty trong
        # file mẫu khách hàng KHÔNG có HS Code riêng (chỉ ~10/55 dòng có). Robot vẫn dùng
        # danh sách HS Code chung (hs_config) để lọc, công ty ở đây chỉ dùng làm từ khóa
        # tìm kiếm (company_name/"keydoc") nên không được bỏ qua các dòng thiếu HS Code.
        hs_raw = row.get(hscode_col, "")
        try:
            # HS Code thường đọc về dạng float (vd 3809.0) → chuẩn hóa về string int
            hs_code = str(int(float(hs_raw))).strip()
        except (TypeError, ValueError):
            hs_code = str(hs_raw).strip()
        if hs_code.upper() == "NAN":
            hs_code = ""

        companies.append({"company_name": name, "hs_code": hs_code})

    if not companies:
        raise ValueError("File không chứa dòng dữ liệu hợp lệ nào (thiếu tên công ty).")

    return companies


def replace_companies(companies: List[Dict]) -> List[Dict]:
    """Ghi đè toàn bộ danh sách công ty (dùng ngay sau khi upload file mới)."""
    _save_raw(companies)
    logger.info("Đã lưu %d công ty mục tiêu.", len(companies))
    return companies
