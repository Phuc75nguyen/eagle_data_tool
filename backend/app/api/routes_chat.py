from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional
import re
from app.services.ai_service import ai_service
from app.services.crawler_service import run_crawl_task
from app.api.routes_auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    status: str
    start: Optional[str] = None
    end: Optional[str] = None
    keyword: Optional[str] = None
    suggested_prompts: List[str] = []

@router.post("/", response_model=ChatResponse)
async def process_chat(req: ChatRequest, background_tasks: BackgroundTasks):
    user_text = req.message
    
    parsed_json = await ai_service.analyze_message(user_text)
    
    status = parsed_json.get("status", "chat")
    start = parsed_json.get("start", "")
    end = parsed_json.get("end", "")
    keyword = parsed_json.get("keyword", "")
    reply = parsed_json.get("reply", "Dạ sếp cần em hỗ trợ xuất dữ liệu gì ạ?")

    # Xử lý bảo vệ cứng: Không có ngày tháng (qua chữ số) -> Báo chat thẳng.
    if not re.search(r'\d', user_text):
        status = "chat"
    
    # Kiểm tra thiếu range
    if status == "ok" and (not start or not end):
        status = "chat"
        reply = "Dạ sếp, để em cào chính xác, sếp vui lòng cho xin ngày bắt đầu và kết thúc nhé."

    if status == "ok":
        background_tasks.add_task(run_crawl_task, start, end, keyword)
        reply = f"Dạ sếp, em đã nhận lệnh và đang cho Robot cào dữ liệu từ {start} đến {end}. Khi nào xong em sẽ báo kết quả nhé!"

    # Refresh hardcoded prompts based on final evaluated status
    suggested = ai_service.get_hardcoded_suggested_prompts(status)

    return ChatResponse(
        reply=reply,
        status=status,
        start=start,
        end=end,
        keyword=keyword,
        suggested_prompts=suggested
    )
