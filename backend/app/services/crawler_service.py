import logging
from app.core.config import load_config, get_credentials
from services.crawler import TradeDataCrawler # We reuse existing TradeDataCrawler from the old services folder
from app.core.database import SessionLocal
from app.services.processor_service import normalize_data

logger = logging.getLogger(__name__)

def run_crawl_task(start_date: str, end_date: str, keyword: str):
    logger.info(f"Background task started: Crawling from {start_date} to {end_date} for keyword: '{keyword}'")
    
    try:
        config = load_config()
        creds = get_credentials()
    except Exception as e:
        logger.error(f"Lỗi đọc file cấu hình: {e}")
        return
        
    try:
        crawler = TradeDataCrawler(config, creds)
        
        if not crawler.login():
            logger.error("Đăng nhập thất bại vào hệ thống crawler.")
            return
            
        data_gen = crawler.fetch_data_generator(start_date, end_date, company_name=keyword, hs_code="")
        
        db = SessionLocal()
        total_inserted = 0
        try:
            for page_data in data_gen:
                if not page_data:
                    continue
                    
                records_to_insert = []
                for item in page_data:
                    # Chuẩn hóa Data lấy từ Processor
                    record = normalize_data(item)
                    records_to_insert.append(record)
                    
                if records_to_insert:
                    db.bulk_save_objects(records_to_insert)
                    db.commit()
                    total_inserted += len(records_to_insert)
                    logger.info(f"Đã lưu {len(records_to_insert)} dòng vào CSDL. Tổng số: {total_inserted}")
                    
            logger.info(f"✅ Quá trình cào dữ liệu cho '{keyword}' hoàn tất! Tổng cộng: {total_inserted} dòng.")
            
        except Exception as e:
            logger.exception(f"Lỗi bất thường khi duyệt và ghi dữ liệu: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.exception(f"Lỗi kết nối crawler service: {e}")
