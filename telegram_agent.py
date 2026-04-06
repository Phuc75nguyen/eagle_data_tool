from telegram.ext.filters import Caption
import os
import json
import asyncio
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import AsyncOpenAI
import glob

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="ollama" 
)

SYSTEM_PROMPT = """
Bạn là Kỹ sư Dữ liệu Ảo thông minh của Eagle Pacific. 
Nhiệm vụ: Phân tích tin nhắn của User và BẮT BUỘC trả về ĐÚNG 1 chuỗi JSON.
TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ BỊA RA NGÀY THÁNG! NẾU USER KHÔNG GHI RÕ NGÀY, BẮT BUỘC ĐỂ TRỐNG "start" VÀ "end".
Cấu trúc JSON:
{
    "status": "ok" (nếu đủ ngày tháng) hoặc "chat" (nếu nói chuyện bình thường),
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD",
    "keyword": "từ khóa sản phẩm/công ty (NẾU KHÔNG CÓ THÌ BẮT BUỘC ĐỂ TRỐNG. Tuyệt đối KHÔNG lấy các từ hành động như 'tải báo cáo', 'lấy dữ liệu' làm từ khóa)",
    "reply": "CÂU TRẢ LỜI CỦA BẠN"
}

HƯỚNG DẪN TẠO CÂU TRẢ LỜI ("reply"):
- Bạn PHẢI ĐỌC HIỂU câu nói của User để trả lời cho đúng ngữ cảnh. KHÔNG ĐƯỢC lặp lại một câu chào máy móc!
- Nếu User chào -> Trả lời: Xin chào sếp ạ!
- Nếu User hỏi "Bạn là ai?" -> Trả lời: "Dạ em là Robot Data của Eagle Pacific ạ."
- Nếu User hỏi "Giúp được gì?" -> Trả lời: "Em có thể giúp sếp tự động tải các báo cáo và dữ liệu nếu sếp cho em ngày tháng ạ."
- Nếu User yêu cầu lấy dữ liệu nhưng thiếu ngày -> Trả lời: "Dạ sếp muốn lấy từ ngày nào đến ngày nào ạ?"

NHỚ KỸ: TRƯỜNG "reply" PHẢI LINH HOẠT THEO TỪNG CÂU HỎI CỦA USER!
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    msg = await update.message.reply_text("🤖 Đang suy nghĩ bằng điện nhà...")

    try:
        response = await client.chat.completions.create(
            model="llama3.2", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.1,
            response_format={"type": "json_object"} 
        )
        
        ai_response = response.choices[0].message.content.strip()
        ai_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL).strip()
        
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:-3].strip()
        elif ai_response.startswith("```"):
            ai_response = ai_response[3:-3].strip()
        
        data = json.loads(ai_response) 
        
        # --- 🛡️ HÀNG RÀO BẢO VỆ TẦNG 1 ---
        status = str(data.get("status") or "").strip()
        start_date = str(data.get("start") or "").strip()
        end_date = str(data.get("end") or "").strip()
        keyword = str(data.get("keyword") or "").strip()
        
        # Chốt chặn "Mù số": Nếu sếp không nhập con số nào, ép thành chat phiếm!
        if not re.search(r'\d', user_text):
            status = "chat"
            start_date = ""
            end_date = ""

        # Chốt chặn "Quên ngày": AI báo ok nhưng thiếu ngày -> Ép quay xe
        if status == "ok" and (not start_date or not end_date or start_date.lower() == "none"):
            status = "chat"
            data["reply"] = "Dạ sếp muốn tải báo cáo từ ngày nào đến ngày nào ạ? Sếp cho em ngày cụ thể nhé."

        # ĐÃ KHÔI PHỤC: Cập nhật dòng "Đang suy nghĩ..." thành câu trả lời của AI
        await msg.edit_text(data.get("reply", "Đang xử lý..."))

        # --- TIẾN HÀNH CHẠY LỆNH NẾU QUA ẢI ---
        if status == "ok":
            command = f'python main.py --start {start_date} --end {end_date}'
            
            # --- LỌC TỪ KHÓA RÁC ---
            bad_keywords = ["tải báo cáo", "lấy dữ liệu", "báo cáo", "từ khóa", "từ khóa (nếu có)", "none", "null"]
            if keyword and keyword.lower() not in bad_keywords:
                command += f' --keyword "{keyword}"'
                
            await update.message.reply_text(f"⚙️ Đang chạy lệnh ngầm: `{command}`\n*(Sếp mở Terminal VS Code lên xem em nó cào data trực tiếp luôn nhé!)*", parse_mode='Markdown')
            
            # --- BƠM THUỐC ÉP PYTHON NHẢ LOG REALTIME ---
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            env["PYTHONUNBUFFERED"] = "1" # Bắt buộc nhả log ngay lập tức, không ngậm trong RAM
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT, # Gom log thường và log lỗi vào chung để dễ đọc
                env=env
            )
            
            run_log = ""
            print(f"\n{'='*40}\n🚀 BẮT ĐẦU CHẠY: {command}\n{'='*40}")
            
            # --- ĐỌC LOG TRỰC TIẾP RA MÀN HÌNH VS CODE ---
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode('utf-8', errors='replace')
                print(decoded_line.strip()) # In thẳng ra Terminal của sếp
                run_log += decoded_line
                
            await process.wait()
            print(f"{'='*40}\n✅ KẾT THÚC LỆNH\n{'='*40}\n")
            
            # KIỂM TRA MÃ TRẢ VỀ CỦA WINDOWS
            if process.returncode == 0:
                short_log = run_log[-800:] if len(run_log) > 800 else run_log
                await update.message.reply_text(f"✅ Tải xong! Tóm tắt log:\n```text\n{short_log}\n```", parse_mode='Markdown')
                
                # --- TÌM VÀ GỬI FILE ---
                OUTPUT_DIR = "./output"
                try:
                    list_of_files = glob.glob(f"{OUTPUT_DIR}/*")
                    list_of_files = [f for f in list_of_files if os.path.isfile(f)]

                    if not list_of_files:
                        await update.message.reply_text(f"⚠️ Quét thư mục '{OUTPUT_DIR}' không thấy file báo cáo nào sếp ạ!")
                    else:
                        latest_file = max(list_of_files, key=os.path.getctime)
                        with open(latest_file, 'rb') as file_to_send:
                            await update.message.reply_document(
                                document=file_to_send, 
                                filename=os.path.basename(latest_file), 
                                caption="📁 Báo cáo sếp yêu cầu đây ạ!"
                            )
                except Exception as e:
                    await update.message.reply_text(f"⚠️ Lỗi bốc file: {str(e)}")
            
            else: # NẾU LỆNH CHẠY THẤT BẠI
                short_error = run_log[-800:] if len(run_log) > 800 else run_log
                await update.message.reply_text(f"❌ Python báo lỗi:\n```text\n{short_error}\n```", parse_mode='Markdown')

    except json.JSONDecodeError:
        await msg.edit_text("⚠️ AI xuất sai định dạng JSON rồi sếp ạ.")
    except Exception as e:
        await msg.edit_text(f"⚠️ Hệ thống bị lỗi: {str(e)}")

def main():
    print("🚀 Đang khởi động Telegram Agent V2 (Powered by Ollama Local)...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot đã sẵn sàng nhận lệnh từ sếp!")
    app.run_polling()

if __name__ == "__main__":
    main()