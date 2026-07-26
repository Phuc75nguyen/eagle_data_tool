"""
app/api/routes_config.py
------------------------
RESTful endpoints để quản lý danh sách HS Code và danh sách công ty mục tiêu.

Routes:
  GET    /api/config/hscodes            → Lấy toàn bộ danh sách HS Code
  POST   /api/config/hscodes            → Thêm một mã mới
  DELETE /api/config/hscodes/{code}     → Xóa một mã

  GET    /api/config/companies          → Lấy danh sách công ty mục tiêu hiện tại
  POST   /api/config/companies/upload   → Upload file Excel (thay thế toàn bộ danh sách)
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, field_validator
from typing import Dict, List

from app.core.hs_config import get_hs_codes, add_hs_code, remove_hs_code
from app.core.company_config import get_companies, parse_company_excel, replace_companies
from app.api.routes_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


# ── Request / Response schemas ───────────────────────────────────────────────

class HsCodeListResponse(BaseModel):
    codes: List[str]
    total: int


class AddHsCodeRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def code_must_be_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("HS Code không được để trống.")
        return v


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/hscodes", response_model=HsCodeListResponse)
def list_hs_codes(user=Depends(get_current_user)):
    """Trả về danh sách HS Code đang được theo dõi."""
    try:
        codes = get_hs_codes()
        return HsCodeListResponse(codes=codes, total=len(codes))
    except Exception as exc:
        logger.exception("Lỗi khi đọc HS Code list: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể đọc danh sách HS Code.")


@router.post("/hscodes", response_model=HsCodeListResponse, status_code=201)
def create_hs_code(payload: AddHsCodeRequest, user=Depends(get_current_user)):
    """Thêm một HS Code mới vào danh sách (trả 409 nếu đã tồn tại)."""
    try:
        updated = add_hs_code(payload.code)
        return HsCodeListResponse(codes=updated, total=len(updated))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.exception("Lỗi khi thêm HS Code '%s': %s", payload.code, exc)
        raise HTTPException(status_code=500, detail="Không thể lưu HS Code.")


@router.delete("/hscodes/{code}", response_model=HsCodeListResponse)
def delete_hs_code(code: str, user=Depends(get_current_user)):
    """Xóa một HS Code khỏi danh sách (trả 404 nếu không tồn tại)."""
    try:
        updated = remove_hs_code(code)
        return HsCodeListResponse(codes=updated, total=len(updated))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Lỗi khi xóa HS Code '%s': %s", code, exc)
        raise HTTPException(status_code=500, detail="Không thể xóa HS Code.")


# ── Companies ────────────────────────────────────────────────────────────────

class CompanyListResponse(BaseModel):
    companies: List[Dict[str, str]]
    total: int


@router.get("/companies", response_model=CompanyListResponse)
def list_companies(user=Depends(get_current_user)):
    """Trả về danh sách công ty mục tiêu đang được cấu hình (rỗng nếu chưa upload)."""
    try:
        companies = get_companies()
        return CompanyListResponse(companies=companies, total=len(companies))
    except Exception as exc:
        logger.exception("Lỗi khi đọc danh sách công ty: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể đọc danh sách công ty.")


@router.post("/companies/upload", response_model=CompanyListResponse, status_code=201)
async def upload_companies(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Upload file Excel danh sách công ty mục tiêu (vd "TEXTILE COMPANY.xlsx").
    Ghi đè toàn bộ danh sách hiện tại — KHÔNG hard-code tên công ty vào mã nguồn.
    """
    filename = (file.filename or "").lower()
    if not (filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file Excel (.xlsx/.xls).")

    try:
        raw_bytes = await file.read()
        companies = parse_company_excel(raw_bytes)
        replace_companies(companies)
        return CompanyListResponse(companies=companies, total=len(companies))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Lỗi khi xử lý file danh sách công ty: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể xử lý file Excel đã upload.")
