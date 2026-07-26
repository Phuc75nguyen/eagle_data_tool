"""
app/services/scheduler_service.py
----------------------------------
Lập lịch tự động kiểm tra dữ liệu tháng mới (Giai đoạn 2 — yêu cầu khách hàng):
  "Lập lịch: Chức năng tự động kiểm tra định kỳ hàng tháng, nếu có dữ liệu
  tháng mới thì tự động thực hiện tiến trình."

Chạy 1 job APScheduler mỗi ngày lúc 03:00 sáng: nếu DB chưa có đủ dữ liệu
tới hết tháng liền trước tháng hiện tại → tự động kích hoạt Robot cào tháng đó.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.trade_record import TradeRecord
from app.services.crawler_service import run_crawl_task
from app.services.month_check import is_data_up_to_date, previous_month_range

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _get_latest_data_date():
    db = SessionLocal()
    try:
        return db.query(func.max(TradeRecord.date)).scalar()
    finally:
        db.close()


def check_and_run_monthly_crawl() -> None:
    """
    Job chạy định kỳ. Kiểm tra xem dữ liệu đã có đủ tháng liền trước tháng
    hiện tại chưa; nếu chưa thì tự động kích hoạt crawl toàn bộ tháng đó.
    """
    start, end = previous_month_range()
    latest_date = _get_latest_data_date()

    if is_data_up_to_date(latest_date):
        logger.info(
            "[Scheduler] Dữ liệu đã cập nhật đến %s, không cần cào thêm tháng %s.",
            latest_date, start.strftime("%Y-%m"),
        )
        return

    logger.info(
        "[Scheduler] Phát hiện thiếu dữ liệu tháng %s (dữ liệu mới nhất: %s) → tự động kích hoạt Robot.",
        start.strftime("%Y-%m"), latest_date,
    )
    try:
        run_crawl_task(start.isoformat(), end.isoformat(), keyword="")
    except Exception:
        logger.exception("[Scheduler] Lỗi khi tự động crawl tháng mới.")


def start_scheduler() -> None:
    """Khởi động scheduler (gọi 1 lần lúc app FastAPI startup)."""
    global _scheduler
    if _scheduler is not None:
        logger.warning("[Scheduler] Đã chạy sẵn, bỏ qua lần khởi động thứ 2.")
        return

    _scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
    _scheduler.add_job(
        check_and_run_monthly_crawl,
        trigger=CronTrigger(hour=3, minute=0),
        id="monthly_crawl_check",
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info("[Scheduler] Đã khởi động — kiểm tra dữ liệu tháng mới mỗi ngày lúc 03:00.")


def stop_scheduler() -> None:
    """Tắt scheduler (gọi lúc app FastAPI shutdown)."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("[Scheduler] Đã tắt.")
