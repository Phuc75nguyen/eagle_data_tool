"""
app/services/month_check.py
----------------------------
Helper dùng chung để xác định xem dữ liệu đã cập nhật đủ tới tháng liền trước
tháng hiện tại hay chưa. Dùng chung bởi:
  - routes_data.py     (API trạng thái + nút "Kiểm tra ngay" thủ công)
  - scheduler_service.py (job tự động chạy định kỳ hàng ngày)
"""

from datetime import date, timedelta
from typing import Optional, Tuple


def previous_month_range(today: Optional[date] = None) -> Tuple[date, date]:
    """Trả về (ngày đầu, ngày cuối) của tháng liền trước tháng chứa `today`."""
    today = today or date.today()
    first_of_this_month = today.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1)
    start = last_day_prev_month.replace(day=1)
    return start, last_day_prev_month


def is_data_up_to_date(latest_date, today: Optional[date] = None) -> bool:
    """
    True nếu dữ liệu trong DB đã có đủ tới hết tháng liền trước tháng hiện tại.

    `latest_date` là ngày mới nhất hiện có trong DB (hoặc None nếu DB rỗng).
    """
    _, end_of_prev_month = previous_month_range(today)
    return bool(latest_date and latest_date >= end_of_prev_month)
