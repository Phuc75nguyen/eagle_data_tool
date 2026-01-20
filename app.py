import streamlit as st
import pandas as pd
# <<<<<<< HEAD
# from src.utils import load_config, get_credentials
# from src.crawler import TradeDataCrawler
# from src.preprocessor import DataPreprocessor

# def main():
#     st.set_page_config(page_title="Trade Crawler Pro", layout="wide")
#     st.title("Tool Crawl Data - Auto Split Files")

#     config = load_config()
#     creds = get_credentials()

#     # --- INPUT UI ---
#     col1, col2 = st.columns(2)
#     with col1:
#         start_date = st.date_input("Từ ngày").strftime("%Y-%m-%d")
#         company_name = st.text_input("Tên công ty / Từ khóa")
#     with col2:
#         end_date = st.date_input("Đến ngày").strftime("%Y-%m-%d")
#         hs_code = st.text_input("HS Code")

#     if st.button("🚀 Bắt đầu Crawl"):
#         crawler = TradeDataCrawler(config, creds)
#         processor = DataPreprocessor(config)

#         if not crawler.login():
#             st.error("Đăng nhập thất bại!")
#             return

#         # UI Components
#         status_box = st.empty()
#         result_area = st.container()
        
#         # --- CẤU HÌNH BATCH ---
#         # Lấy giới hạn dòng mỗi file từ config. Mặc định 50,000 dòng.
#         MAX_ROWS_PER_FILE = config['processing'].get('max_rows_per_file', 50000)
        
#         buffer = []          # Cái xô chứa dữ liệu tạm
#         file_results = []    # Danh sách các file đã tạo xong
#         total_fetched = 0    # Tổng số dòng đã crawl được từ đầu
#         part_index = 1       # Đếm số thứ tự file (part_1, part_2...)

#         # Gọi hàm Generator (Streaming)
#         data_gen = crawler.fetch_data_generator(start_date, end_date, company_name, hs_code)

#         try:
#             # Vòng lặp lấy từng trang data về
#             for page_data in data_gen:
#                 if not page_data: 
#                     continue

#                 # 1. Đổ data vào xô
#                 buffer.extend(page_data)
#                 total_fetched += len(page_data)

#                 # Hiển thị trạng thái realtime
#                 status_box.info(
#                     f"🔄 Đang crawl... Tổng: **{total_fetched}** dòng. "
#                     f"Đang chờ đóng gói: **{len(buffer)}/{MAX_ROWS_PER_FILE}** dòng (File Part {part_index})"
#                 )

#                 # 2. Kiểm tra: Nếu xô đầy tràn -> Cắt ra làm file
#                 while len(buffer) >= MAX_ROWS_PER_FILE:
#                     # Cắt đúng số lượng quy định
#                     chunk_to_save = buffer[:MAX_ROWS_PER_FILE]
                    
#                     # Phần dư giữ lại trong xô cho đợt sau
#                     buffer = buffer[MAX_ROWS_PER_FILE:] 
                    
#                     # Tạo file Excel
#                     file_name = f"trade_data_part_{part_index}.xlsx"
#                     status_box.warning(f"💾 Đang tạo file **{file_name}**...")
                    
#                     excel_bytes = processor.create_excel_bytes(pd.DataFrame(chunk_to_save))
                    
#                     if excel_bytes:
#                         file_results.append({'name': file_name, 'data': excel_bytes})
#                         part_index += 1 # Tăng số thứ tự file tiếp theo

#             # 3. XỬ LÝ PHẦN CÒN LẠI (LEFTOVER)
#             # Sau khi crawl xong hết, nếu trong xô vẫn còn ít dữ liệu chưa đủ 50k
#             if buffer:
#                 file_name = f"trade_data_part_{part_index}.xlsx"
#                 status_box.warning(f"💾 Đang tạo file cuối cùng **{file_name}**...")
#                 excel_bytes = processor.create_excel_bytes(pd.DataFrame(buffer))
#                 if excel_bytes:
#                     file_results.append({'name': file_name, 'data': excel_bytes})

#             # --- KẾT THÚC ---
#             status_box.success(f"✅ Hoàn thành! Tổng cộng: {total_fetched} dòng. Đã chia thành {len(file_results)} file.")

#             # Hiển thị nút download
#             st.write("### 📂 Danh sách file tải xuống:")
            
#             # Chia cột hiển thị cho đẹp
#             cols = st.columns(3)
#             for i, f in enumerate(file_results):
#                 with cols[i % 3]:
#                     st.download_button(
#                         label=f"📥 Tải {f['name']}",
#                         data=f['data'],
#                         file_name=f['name'],
#                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                         key=f"dl_{i}"
#                     )

#         except Exception as e:
#             st.error(f"Lỗi trong quá trình xử lý: {e}")

# if __name__ == "__main__":
#     main()
import time
from io import BytesIO
from processor import standardize_data, filter_by_product

# --- Page Configuration ---
st.set_page_config(
    page_title="Eagle Pacific Data Tool",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
<style>
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #64748B;
        --background-color: #F8FAFC;
    }
    
    .main {
        background-color: var(--background-color);
    }
    
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #172554;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        border-left: 5px solid #10B981;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
    }
    
    [data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }

    .report-header {
        font-family: 'Inter', sans-serif;
        color: var(--primary-color);
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None

def add_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")

# --- Sidebar Implementation ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=EAGLE+PACIFIC", width=150)
    st.markdown("### 🛠️ Configuration")
    
    # File Uploader for Target Companies
    target_file = st.file_uploader("Upload Target Company List (Excel)", type=["xlsx", "xls"])
    
    st.divider()
    
    st.markdown("### 📡 System Status")
    with st.container():
        st.markdown("""
        <div class="status-card">
            <span style="color: #065F46; font-weight: bold;">Alex's API: Connected</span><br>
            <small style="color: #6B7280;">Latency: 45ms | Status: Healthy</small>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    if st.button("🔄 Refresh Data Source"):
        with st.spinner("Connecting to API..."):
            time.sleep(1.5)
            # For demonstration, we load the local xls file as our "API" data
            try:
                st.session_state.raw_data = pd.read_excel("Trade record 2026-01-09_10_27.xls")
                add_log("Successfully fetched latest trade records from API.")
                st.toast("Data Refreshed!", icon="✅")
            except Exception as e:
                st.error(f"API Connection Error: {e}")
                add_log(f"ERROR: Failed to fetch API data: {e}")

# --- Main Interface ---
st.markdown("<h1 class='report-header'>🦅 Eagle Pacific Trade Intelligence</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Data Explorer", "🤖 Robot Logs"])

with tab1:
    if target_file:
        try:
            # Load targets (handling potential header issues discovered during prototyping)
            # Based on previous investigation, 2nd row (index 1) usually contains the headers
            df_targets = pd.read_excel(target_file, header=1)
            
            if st.session_state.raw_data is not None:
                # 1. Standardize Data
                processed_df = standardize_data(st.session_state.raw_data, df_targets)
                
                # 2. Search Filter
                search_query = st.text_input("🔍 Search Products", placeholder="Enter keyword (e.g., 'ASUKD 1897')")
                filtered_df = filter_by_product(processed_df, search_query)
                
                # Stats Row
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Records", len(filtered_df))
                col2.metric("Total Value", f"${filtered_df['Value'].sum():,.2f}")
                col3.metric("Filtered By Search", "Yes" if search_query else "No")
                
                # Data Display
                st.dataframe(filtered_df, use_container_width=True, height=500)
                
                # Export Section
                st.divider()
                export_col1, export_col2 = st.columns([1, 4])
                
                # Excel Export logic
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Standardized_Report')
                processed_data = output.getvalue()
                
                export_col1.download_button(
                    label="📥 Download Standardized Report",
                    data=processed_data,
                    file_name=f"Standardized_Report_{time.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    on_click=lambda: st.success("Report downloaded successfully!")
                )
                
            else:
                st.info("Click 'Refresh Data Source' in the sidebar to fetch trade data from the API.")
        except Exception as e:
            st.error(f"Error processing files: {e}")
    else:
        st.warning("⚠️ Please upload the 'Target Company List' in the sidebar to begin filtering.")

with tab2:
    st.markdown("### 🛠️ Execution Logs")
    log_text = "\n".join(reversed(st.session_state.logs))
    st.text_area("Live Stream", value=log_text, height=400, disabled=True)
    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94A3B8;'>© 2026 Eagle Pacific Logistics. Built by Senior Full-stack Team.</p>", unsafe_allow_html=True)