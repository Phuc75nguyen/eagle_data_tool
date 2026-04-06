import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, config):
        self.config = config
        self.extract_cols = config.get('columns_to_extract', [])
        self.mapping = config.get('column_mapping', {})
        self.padding = config['processing'].get('padding_size', 2)
        self.target_col = config['processing'].get('target_column', 'price')
        self.max_col_width = config['processing'].get('max_column_width', 40)

    def create_excel_bytes(self, df):
        """
        Biến đổi DataFrame thành file Excel (lưu trong RAM).
        
        INPUT:
        - df: DataFrame chứa dữ liệu cần ghi vào file.
        
        OUTPUT:
        - io.BytesIO: Đối tượng file nhị phân (dùng để gán vào nút Download).
        - Trả về None nếu df rỗng hoặc lỗi.
        """
        if df.empty:
            return None

        # --- GIAI ĐOẠN 1: CLEAN DATA ---
        # 1. Lọc cột
        existing_cols = [col for col in self.extract_cols if col in df.columns]
        df_clean = df[existing_cols].copy() # Dùng .copy() để tránh warning SettingWithCopy

        # 2. Format số tiền
        if self.target_col in df_clean.columns:
            try:
                df_clean[self.target_col] = pd.to_numeric(df_clean[self.target_col], errors='coerce')
                df_clean[self.target_col] = df_clean[self.target_col].map('{:,.2f}'.format)
            except Exception:
                pass

        # 3. Rename cột
        df_clean = df_clean.rename(columns=self.mapping)

        # --- GIAI ĐOẠN 2: WRITE EXCEL ---
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_clean.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # Format Header & Column Width (Code cũ của bạn)
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'fg_color': '#1E9F96',
                    'border': 1, 'align': 'center', 'valign': 'vcenter'
                })
                
                for col_num, value in enumerate(df_clean.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                for i, col in enumerate(df_clean.columns):
                    header_len = len(str(col))
                    max_data_len = 0
                    if not df_clean[col].empty:
                        max_data_len = df_clean[col].astype(str).map(len).max()
                    
                    final_width = min(max(header_len, max_data_len) + self.padding, self.max_col_width)
                    worksheet.set_column(i, i, final_width)

            output.seek(0)
            return output
        except Exception as e:
            logger.error(f"Lỗi tạo Excel: {e}")
            return None