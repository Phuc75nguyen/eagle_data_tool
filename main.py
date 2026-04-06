import argparse
import logging
import pandas as pd
import os
from src.crawler import TradeDataCrawler
from src.preprocessor import DataPreprocessor
from src.utils import load_config, get_credentials

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Data Tool cho Eagle Pacific")
    parser.add_argument("--start", type=str, required=True, help="Ngày bắt đầu (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="Ngày kết thúc (YYYY-MM-DD)")
    parser.add_argument("--keyword", type=str, default="", help="Từ khóa sản phẩm")
    
    args = parser.parse_args()
    logging.info(f"Kích hoạt tải dữ liệu: {args.start} -> {args.end} | Keyword: {args.keyword}")
    
    # 1. Đọc file cấu hình và tài khoản
    try:
        config = load_config()
        creds = get_credentials()
    except Exception as e:
        logging.error(f"Lỗi đọc file cấu hình: {e}")
        exit(1) # Báo lỗi văng ra ngoài cho Telegram Bot biết
    
    # 2. Khởi tạo đồ nghề
    crawler = TradeDataCrawler(config, creds)
    processor = DataPreprocessor(config)
    
    # 3. Đăng nhập API
    if not crawler.login():
        logging.error("Đăng nhập thất bại! Sếp check lại mật khẩu trong secrets.toml nhé.")
        exit(1)
        
    # 4. Tạo thư mục output nếu chưa có (Để Bot chui vào lấy)
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Dọn dẹp file cũ trong thư mục output trước khi chạy mới (Tránh gửi nhầm file cũ)
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))
    
    # 5. Bắt đầu Crawl Data (Truyền args.keyword vào search)
    data_gen = crawler.fetch_data_generator(args.start, args.end, company_name=args.keyword, hs_code="")
    
    buffer = []
    MAX_ROWS_PER_FILE = config['processing'].get('max_rows_per_file', 50000)
    part_index = 1
    total_fetched = 0
    
    try:
        for page_data in data_gen:
            if not page_data: 
                continue
            
            buffer.extend(page_data)
            total_fetched += len(page_data)
            
            # Nếu xô đầy -> Lưu ra file Excel
            while len(buffer) >= MAX_ROWS_PER_FILE:
                chunk = buffer[:MAX_ROWS_PER_FILE]
                buffer = buffer[MAX_ROWS_PER_FILE:] 
                
                file_name = os.path.join(output_dir, f"TradeData_{args.start}_part_{part_index}.xlsx")
                excel_bytes = processor.create_excel_bytes(pd.DataFrame(chunk))
                
                if excel_bytes:
                    # Ghi BytesIO xuống ổ cứng
                    with open(file_name, "wb") as f:
                        f.write(excel_bytes.getvalue())
                    logging.info(f"Đã lưu: {file_name}")
                
                part_index += 1

        # Lưu phần dư còn lại
        if buffer:
            file_name = os.path.join(output_dir, f"TradeData_{args.start}_part_{part_index}.xlsx")
            excel_bytes = processor.create_excel_bytes(pd.DataFrame(buffer))
            if excel_bytes:
                with open(file_name, "wb") as f:
                    f.write(excel_bytes.getvalue())
                logging.info(f"Đã lưu file cuối: {file_name}")
                
        logging.info(f"✅ Hoàn thành xuất sắc! Tổng cộng: {total_fetched} dòng dữ liệu.")
        
    except Exception as e:
        logging.error(f"Lỗi khi đang lấy dữ liệu: {e}")
        exit(1)

if __name__ == "__main__":
    main()