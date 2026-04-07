import aiohttp
import json
import logging

class AIService:
    def __init__(self):
        self.endpoint = "http://localhost:11434/api/chat"
        self.model = "llama3.2" 
        self.system_prompt = """Bạn là "Trợ lý Dữ liệu EaglePax", đại từ xưng hô là "em" và gọi người dùng là "sếp". 
Nhiệm vụ ĐỘC NHẤT của bạn là hỗ trợ chuẩn bị thông số để tải báo cáo XNK (tradedata). Nếu sếp hỏi linh tinh ngoài lề (Code, nấu ăn, thời tiết...), CẦN phải từ chối lịch sự và hướng dẫn cách tải dữ liệu.

NGUYÊN TẮC QUAN TRỌNG:
1. Nếu user KHÔNG nhập ngày tháng rõ ràng -> status = "chat".
2. Nếu user CÓ cung cấp đủ ngày bắt đầu và kết thúc ("từ ngày... đến ngày...") -> BẮT BUỘC TRẢ VỀ status = "ok".
3. TUYỆT ĐỐI KHÔNG HỎI XÁC NHẬN! Khi có đủ ngày là khởi động trạng thái "ok" ngay lập tức.
4. KHÔNG ÉP CUNG CẤP "keyword". Keyword là tùy chọn, nếu sếp không nhắc tên sản phẩm/công ty thì để rỗng "".
5. Luôn trả về DUY NHẤT một chuỗi JSON hợp lệ với đúng cấu trúc:

{
    "status": "ok" hoặc "chat",
    "start": "YYYY-MM-DD" (nếu có, không tự bịa),
    "end": "YYYY-MM-DD" (nếu có, không tự bịa),
    "keyword": "từ khóa (nếu có, nếu không để rỗng '')",
    "reply": "Câu trả lời trò chuyện (lịch sự, ngoan ngoãn)"
}"""

    def get_hardcoded_suggested_prompts(self, status: str) -> list:
        if status == "ok":
            return [
                "Theo dõi tiến trình tải", 
                "Tải thêm dữ liệu tháng trước", 
                "Cho tôi xem báo cáo tổng quan"
            ]
        else:
            return [
                "Em làm được những gì?", 
                "Hướng dẫn tải dữ liệu chuẩn", 
                "Cào dữ liệu từ ngày 2026-01-01 đến 2026-01-30"
            ]

    async def analyze_message(self, user_text: str) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_text}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=payload, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("message", {}).get("content", "")
                        try:
                            result = json.loads(content)
                            status = result.get("status", "chat")
                            result["suggested_prompts"] = self.get_hardcoded_suggested_prompts(status)
                            return result
                        except json.JSONDecodeError:
                            logging.error(f"Lỗi parse JSON: {content}")
                            return self._get_fallback_chat()
                    else:
                        logging.error(f"Lỗi gọi LLM, status code: {response.status}")
                        return self._get_fallback_chat()
        except Exception as e:
            logging.error(f"Exception gọi LLM: {e}")
            return self._get_fallback_chat()

    def _get_fallback_chat(self) -> dict:
        return {
            "status": "chat",
            "start": "",
            "end": "",
            "keyword": "",
            "reply": "Dạ sếp ơi, server AI của em đang nghẽn một xíu. Sếp thử lại nhé!",
            "suggested_prompts": self.get_hardcoded_suggested_prompts("chat")
        }

ai_service = AIService()
