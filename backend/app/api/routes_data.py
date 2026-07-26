from fastapi import APIRouter, Depends, Query, HTTPException, Request, BackgroundTasks
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import asyncio
import json
import pandas as pd
import io
import logging

from app.core.database import get_db, SessionLocal
from app.core.progress_log import _crawl_log_queue
from app.models.trade_record import TradeRecord
from app.api.routes_auth import get_current_user
from app.services.crawler_service import run_crawl_task
from app.services.month_check import is_data_up_to_date, previous_month_range

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])


# ---------------------------------------------------------------------------
# GET /api/data/status  (giữ nguyên cho backward compat — không dùng SSE)
# ---------------------------------------------------------------------------
@router.get("/status")
def get_data_status(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Trả về số bản ghi hiện tại, ngày cập nhật gần nhất, và cảnh báo tháng mới
    (needs_update = True nếu DB chưa có đủ dữ liệu tới hết tháng liền trước
    tháng hiện tại — dùng để hiển thị banner cảnh báo trên UI).
    """
    total = db.query(func.count(TradeRecord.id)).scalar() or 0
    latest = db.query(func.max(TradeRecord.date)).scalar()

    start, _ = previous_month_range()
    up_to_date = is_data_up_to_date(latest)

    return {
        "total_records": total,
        "last_updated": str(latest) if latest else None,
        "has_data": total > 0,
        "needs_update": not up_to_date,
        "missing_month": None if up_to_date else start.strftime("%Y-%m"),
    }


# ---------------------------------------------------------------------------
# POST /api/data/crawl/check-new-month — nút "Kiểm tra & cào dữ liệu tháng mới"
# Dùng chung logic với scheduler tự động (app/services/scheduler_service.py).
# ---------------------------------------------------------------------------
@router.post("/crawl/check-new-month")
def trigger_new_month_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Kiểm tra ngay xem có thiếu dữ liệu tháng liền trước không; nếu có thì kích hoạt Robot."""
    latest = db.query(func.max(TradeRecord.date)).scalar()
    start, end = previous_month_range()

    if is_data_up_to_date(latest):
        return {
            "triggered": False,
            "message": f"Dữ liệu đã cập nhật đến {latest}. Không cần cào thêm.",
            "missing_month": None,
        }

    background_tasks.add_task(run_crawl_task, start.isoformat(), end.isoformat(), "")
    return {
        "triggered": True,
        "message": f"Đã kích hoạt Robot cào dữ liệu tháng {start.strftime('%m/%Y')}.",
        "missing_month": start.strftime("%Y-%m"),
    }


# ---------------------------------------------------------------------------
# GET /api/data/stream   — Server-Sent Events: realtime crawl progress
# ---------------------------------------------------------------------------
@router.get("/stream")
async def stream_crawl_progress(request: Request, user=Depends(get_current_user)):
    """
    SSE endpoint.  Frontend kết nối một lần bằng EventSource,
    backend liên tục yield event mỗi khi crawler push log mới.

    Event format (text/event-stream):
        data: {"type": "log", "message": "HS 3809: Trang 3 +10 dòng"}\\n\\n
        data: {"type": "done", "total_records": 420}\\n\\n
    """
    async def event_generator():
        logger.info("SSE client connected: %s", request.client)
        try:
            while True:
                # Kiểm tra client ngắt kết nối
                if await request.is_disconnected():
                    logger.info("SSE client disconnected.")
                    break

                try:
                    # Chờ tối đa 2s cho message tiếp theo
                    message = await asyncio.wait_for(_crawl_log_queue.get(), timeout=2.0)
                    payload = json.dumps({"type": "log", "message": message}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"

                except asyncio.TimeoutError:
                    # Heartbeat giữ kết nối sống (tránh proxy timeout)
                    yield ": heartbeat\n\n"

        except Exception as exc:
            logger.exception("SSE generator error: %s", exc)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # tắt buffer ở Nginx
        },
    )

@router.get("/")
def get_data(
    skip: int = Query(0, description="Pagination skip"),
    limit: int = Query(20, description="Pagination limit"),
    keyword: str = Query(None, description="Search keyword matching importer or product"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(TradeRecord)
    
    if keyword:
        query = query.filter(
            or_(
                TradeRecord.importer.ilike(f"%{keyword}%"),
                TradeRecord.product.ilike(f"%{keyword}%"),
                TradeRecord.hs_code.ilike(f"%{keyword}%")
            )
        )
        
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": records
    }

@router.get("/export")
def export_data(
    keyword: str = Query(None, description="Search keyword matching importer or product"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(TradeRecord)
    if keyword:
        query = query.filter(
            or_(
                TradeRecord.importer.ilike(f"%{keyword}%"),
                TradeRecord.product.ilike(f"%{keyword}%"),
                TradeRecord.hs_code.ilike(f"%{keyword}%")
            )
        )
        
    records = query.all()
    if not records:
        raise HTTPException(status_code=404, detail="No data found to export.")
        
    # Convert to standard dict list
    data_list = []
    for r in records:
        data_list.append({
            "Date": r.date.isoformat() if r.date else "",
            "Importer": r.importer,
            "HsCode": r.hs_code,
            "Product": r.product,
            "Quantity": r.quantity,
            "QuantityUnit": r.quantity_unit,
            "Value": r.value,
            "ValueUnit": r.value_unit,
            "UnitPrice": r.unit_price
        })
        
    df = pd.DataFrame(data_list)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trade Data')
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="exported_data.xlsx"'
    }
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
