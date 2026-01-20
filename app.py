import streamlit as st
import pandas as pd
from src.utils import load_config, get_credentials
from src.crawler import TradeDataCrawler
from src.preprocessor import DataPreprocessor

def main():
    st.set_page_config(page_title="Trade Crawler Pro", layout="wide")
    st.title("Tool Crawl Data - Auto Split Files")

    config = load_config()
    creds = get_credentials()

    # --- INPUT UI ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Từ ngày").strftime("%Y-%m-%d")
        company_name = st.text_input("Tên công ty / Từ khóa")
    with col2:
        end_date = st.date_input("Đến ngày").strftime("%Y-%m-%d")
        hs_code = st.text_input("HS Code")

    if st.button("🚀 Bắt đầu Crawl"):
        crawler = TradeDataCrawler(config, creds)
        processor = DataPreprocessor(config)

        if not crawler.login():
            st.error("Đăng nhập thất bại!")
            return

        # UI Components
        status_box = st.empty()
        result_area = st.container()
        
        # --- CẤU HÌNH BATCH ---
        # Lấy giới hạn dòng mỗi file từ config. Mặc định 50,000 dòng.
        MAX_ROWS_PER_FILE = config['processing'].get('max_rows_per_file', 50000)
        
        buffer = []          # Cái xô chứa dữ liệu tạm
        file_results = []    # Danh sách các file đã tạo xong
        total_fetched = 0    # Tổng số dòng đã crawl được từ đầu
        part_index = 1       # Đếm số thứ tự file (part_1, part_2...)

        # Gọi hàm Generator (Streaming)
        data_gen = crawler.fetch_data_generator(start_date, end_date, company_name, hs_code)

        try:
            # Vòng lặp lấy từng trang data về
            for page_data in data_gen:
                if not page_data: 
                    continue

                # 1. Đổ data vào xô
                buffer.extend(page_data)
                total_fetched += len(page_data)

                # Hiển thị trạng thái realtime
                status_box.info(
                    f"🔄 Đang crawl... Tổng: **{total_fetched}** dòng. "
                    f"Đang chờ đóng gói: **{len(buffer)}/{MAX_ROWS_PER_FILE}** dòng (File Part {part_index})"
                )

                # 2. Kiểm tra: Nếu xô đầy tràn -> Cắt ra làm file
                while len(buffer) >= MAX_ROWS_PER_FILE:
                    # Cắt đúng số lượng quy định
                    chunk_to_save = buffer[:MAX_ROWS_PER_FILE]
                    
                    # Phần dư giữ lại trong xô cho đợt sau
                    buffer = buffer[MAX_ROWS_PER_FILE:] 
                    
                    # Tạo file Excel
                    file_name = f"trade_data_part_{part_index}.xlsx"
                    status_box.warning(f"💾 Đang tạo file **{file_name}**...")
                    
                    excel_bytes = processor.create_excel_bytes(pd.DataFrame(chunk_to_save))
                    
                    if excel_bytes:
                        file_results.append({'name': file_name, 'data': excel_bytes})
                        part_index += 1 # Tăng số thứ tự file tiếp theo

            # 3. XỬ LÝ PHẦN CÒN LẠI (LEFTOVER)
            # Sau khi crawl xong hết, nếu trong xô vẫn còn ít dữ liệu chưa đủ 50k
            if buffer:
                file_name = f"trade_data_part_{part_index}.xlsx"
                status_box.warning(f"💾 Đang tạo file cuối cùng **{file_name}**...")
                excel_bytes = processor.create_excel_bytes(pd.DataFrame(buffer))
                if excel_bytes:
                    file_results.append({'name': file_name, 'data': excel_bytes})

            # --- KẾT THÚC ---
            status_box.success(f"✅ Hoàn thành! Tổng cộng: {total_fetched} dòng. Đã chia thành {len(file_results)} file.")

            # Hiển thị nút download
            st.write("### 📂 Danh sách file tải xuống:")
            
            # Chia cột hiển thị cho đẹp
            cols = st.columns(3)
            for i, f in enumerate(file_results):
                with cols[i % 3]:
                    st.download_button(
                        label=f"📥 Tải {f['name']}",
                        data=f['data'],
                        file_name=f['name'],
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{i}"
                    )

        except Exception as e:
            st.error(f"Lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()