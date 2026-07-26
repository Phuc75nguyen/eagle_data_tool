"""
app/services/crawler_service.py
--------------------------------
Background task: lấy danh sách HS Code từ hs_config, cào dữ liệu theo từng mã,
lọc gắt qua processor, rồi batch-insert vào CSDL.

Design principles:
  - KHÔNG hard-code HS Code trong file này.
  - Xử lý Exception đầy đủ ở từng bước.
  - Chống block: sleep giữa các mã HS và giữa các trang.
  - Gom toàn bộ record của TẤT CẢ mã HS vào one list trước khi filter+save.
"""

import time
import logging
from typing import List, Dict

from app.core.config import load_config, get_credentials
from app.core.hs_config import get_hs_codes
from app.core.company_config import get_company_names
from app.core.database import SessionLocal
from app.services.crawler import TradeDataCrawler
from app.services.processor_service import strict_hscode_filter, normalize_data
from app.core.progress_log import push_crawl_log

logger = logging.getLogger(__name__)

# Số giây nghỉ giữa hai mã HS để tránh bị throttle / block
_INTER_CODE_SLEEP: float = 2.0


def run_crawl_task(start_date: str, end_date: str, keyword: str = "") -> None:
    """
    Background task entry point.

    Flow:
      1. Đọc TARGET_HS_CODES từ hs_config (không hard-code).
      2. Đăng nhập TradeData một lần duy nhất.
      3. Với mỗi hs_code → cào tất cả trang → gom vào all_records.
      4. Lọc gắt all_records qua strict_hscode_filter.
      5. Chuẩn hóa → bulk-insert vào DB.
    """
    logger.info(
        "=== BẮT ĐẦU CRAWL: %s → %s | keyword='%s' ===",
        start_date, end_date, keyword,
    )

    # ── 1. Lấy danh sách HS Code ─────────────────────────────────────────────
    try:
        target_hscodes: List[str] = get_hs_codes()
    except Exception as exc:
        logger.error("Không đọc được HS Code list: %s", exc)
        return

    if not target_hscodes:
        logger.warning("Danh sách HS Code rỗng. Dừng crawl.")
        return

    logger.info("Sẽ cào %d mã HS: %s", len(target_hscodes), target_hscodes)

    # ── 1b. Nếu không có keyword thủ công (từ chat) → dùng danh sách công ty đã
    # upload làm bộ lọc mặc định. API TradeData hỗ trợ nhận nhiều công ty trong
    # cùng 1 lần gọi, phân cách bởi dấu ';' (xem docstring fetch_data_generator).
    if not keyword:
        company_names = get_company_names()
        if company_names:
            keyword = ";".join(company_names)
            logger.info(
                "Không có keyword thủ công → dùng %d công ty từ danh sách đã upload.",
                len(company_names),
            )
        else:
            logger.info("Không có keyword và chưa upload danh sách công ty nào → cào theo HS Code trên toàn bộ thị trường.")

    # ── 2. Đọc config & đăng nhập ────────────────────────────────────────────
    try:
        config = load_config()
        creds = get_credentials()
    except Exception as exc:
        logger.error("Lỗi đọc file cấu hình: %s", exc)
        return

    try:
        crawler = TradeDataCrawler(config, creds)
        if not crawler.login():
            logger.error("Đăng nhập thất bại vào hệ thống TradeData. Dừng crawl.")
            return
    except Exception as exc:
        logger.exception("Không khởi tạo được TradeDataCrawler: %s", exc)
        return

    # ── 3. Cào dữ liệu theo từng mã HS ───────────────────────────────────────
    all_records: List[Dict] = []

    for idx, hs_code in enumerate(target_hscodes, start=1):
        logger.info("[%d/%d] Bắt đầu cào HS Code: %s", idx, len(target_hscodes), hs_code)

        try:
            page_count = 0
            code_records: List[Dict] = []

            for page_data in crawler.fetch_data_generator(
                start_date=start_date,
                end_date=end_date,
                company_name=keyword,
                hs_code=hs_code,
            ):
                if not page_data:
                    continue
                code_records.extend(page_data)
                page_count += 1

                # ── Push SSE progress event ──────────────────────────────
                push_crawl_log(
                    f"HS {hs_code}: Đã cào xong trang {page_count} (+{len(page_data)} dòng)"
                )

            logger.info(
                "HS Code %s: cào xong %d trang, %d dòng thô.",
                hs_code, page_count, len(code_records),
            )
            push_crawl_log(f"HS {hs_code}: Hoàn tất — {len(code_records)} dòng thô.")
            all_records.extend(code_records)

        except Exception as exc:
            logger.exception("Lỗi khi cào HS Code '%s': %s", hs_code, exc)
            # Tiếp tục với mã tiếp theo thay vì dừng toàn bộ

        # Chống block: nghỉ giữa các mã HS (trừ mã cuối cùng)
        if idx < len(target_hscodes):
            logger.debug("Nghỉ %.1fs trước mã HS tiếp theo...", _INTER_CODE_SLEEP)
            time.sleep(_INTER_CODE_SLEEP)

    logger.info(
        "Cào xong tất cả mã. Tổng dòng thô: %d. Bắt đầu filter & lưu DB...",
        len(all_records),
    )

    if not all_records:
        logger.warning("Không có dữ liệu nào được cào về. Kết thúc.")
        return

    # ── 4. Lọc gắt ──────────────────────────────────────────────────────────
    try:
        filtered_records = strict_hscode_filter(all_records, target_hscodes)
    except Exception as exc:
        logger.exception("Lỗi trong strict_hscode_filter: %s", exc)
        return

    if not filtered_records:
        logger.warning("Sau khi filter, không còn record hợp lệ. Kết thúc.")
        return

    # ── 5. Chuẩn hóa & lưu DB ────────────────────────────────────────────────
    db = SessionLocal()
    total_inserted = 0
    batch_size = 200   # Insert theo batch để tránh OOM

    try:
        batch: List = []
        for raw_item in filtered_records:
            try:
                record = normalize_data(raw_item)
                batch.append(record)
            except Exception as exc:
                logger.warning("Bỏ qua 1 record lỗi normalize: %s | item=%s", exc, raw_item)
                continue

            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                total_inserted += len(batch)
                logger.info("Đã lưu batch %d dòng (tổng: %d).", len(batch), total_inserted)
                batch = []

        # Lưu phần còn dư
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            total_inserted += len(batch)

    except Exception as exc:
        logger.exception("Lỗi bất thường khi ghi DB: %s", exc)
        db.rollback()
    finally:
        db.close()

    logger.info(
        "=== CRAWL HOÀN TẤT. Tổng dòng đã lưu: %d / %d (sau filter). ===",
        total_inserted, len(filtered_records),
    )
    # ── Push final "done" event ──────────────────────────────────────
    push_crawl_log(f"__DONE__:{total_inserted}")
