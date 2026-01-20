import os
import logging
import sys
from logging.handlers import RotatingFileHandler

# 1. Cấu hình nơi lưu log
LOG_DIR = "logs"
LOG_FILE = "app.log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 2. Định dạng log (Format)
# Cấu trúc: [Thời gian] [Tên module] [Level] Nội dung
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    """
    Thiết lập cấu hình logging cho toàn bộ ứng dụng.
    Hàm này đảm bảo log được ghi vào cả file và console.
    """
    # Lấy root logger
    root_logger = logging.getLogger()
    
    # Nếu logger đã có handler rồi (do Streamlit reload) thì không add thêm để tránh duplicate log
    if root_logger.hasHandlers():
        return

    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Handler 1: Ghi ra file (tự động xoay vòng file khi file quá lớn - 5MB)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=5*1024*1024, # 5MB
        backupCount=3,        # Giữ lại 3 file cũ
        encoding='utf-8'      # Quan trọng: Hỗ trợ tiếng Việt
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Handler 2: Ghi ra màn hình Console (Terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info(f"Logging đã được khởi tạo. File log tại: {os.path.join(LOG_DIR, LOG_FILE)}")

# Tự động chạy setup khi import package src
setup_logging()