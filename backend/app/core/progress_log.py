"""
app/core/progress_log.py
--------------------------
Hàng đợi log tiến trình crawl dùng chung, tách riêng khỏi routes_data.py để
tránh circular import (crawler_service cần push log, routes_data cần cả
push_crawl_log lẫn run_crawl_task).

crawler_service.py / scheduler_service.py → push_crawl_log() để đẩy message.
routes_data.py (endpoint /stream) → pop message ra để stream SSE cho client.
"""

import asyncio

_crawl_log_queue: asyncio.Queue = asyncio.Queue(maxsize=200)


def push_crawl_log(message: str) -> None:
    """Đẩy 1 dòng log tiến trình crawl vào hàng đợi (thread-safe, non-blocking)."""
    try:
        _crawl_log_queue.put_nowait(message)
    except asyncio.QueueFull:
        pass  # drop — tránh OOM khi client chưa consume kịp
