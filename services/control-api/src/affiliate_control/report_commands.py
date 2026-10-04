"""Explicit owner observations; never attribute account totals to individual videos."""
from datetime import date
import math
import uuid

from affiliate_domain.two_video import stamp, text
from .content_commands import find


FIELDS = {"product_id", "period_start", "period_end", "report_reference", "clicks", "pending_orders",
          "approved_orders", "total_orders", "estimated_commission", "pending_commission", "approved_commission", "paid_amount"}


def save(state, data):
    product_id = data.get("product_id") or None
    if product_id:
        find(state["products"], product_id)
    start, end = date.fromisoformat(data["period_start"]), date.fromisoformat(data["period_end"])
    if start > end or end > date.today():
        raise ValueError("Kỳ báo cáo chưa hợp lệ hoặc ở tương lai.")
    record = {"id": str(uuid.uuid4()), "product_id": product_id, "period_start": str(start),
              "period_end": str(end), "report_reference": text(data["report_reference"], 180),
              "source": "owner_report_not_api_verified", "observed_at": stamp(), "currency": "VND"}
    for field in FIELDS - {"product_id", "period_start", "period_end", "report_reference"}:
        value = data.get(field)
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0 or value > 1e12):
            raise ValueError("Chỉ số phải là số không âm; để trống nếu chưa có dữ liệu.")
        if value is not None and field in ("clicks", "pending_orders", "approved_orders", "total_orders") and int(value) != value:
            raise ValueError("Click/đơn hàng phải là số nguyên.")
        record[field] = value
    reports = state.setdefault("affiliate_reports", [])
    reports[:] = [r for r in reports if (r["product_id"], r["period_start"], r["period_end"]) != (product_id, str(start), str(end))]
    if len(reports) >= 200:
        raise ValueError("Đã đủ 200 kỳ báo cáo; cần lưu trữ trước khi thêm.")
    reports.append(record)
    return {"report_id": record["id"]}


def post_control(state, data):
    ident = text(data["video_id"], 11)
    choice = data["choice"]
    if choice not in ("hide", "restore", "request_delete", "cancel_delete", "bind"):
        raise ValueError("Thao tác bài đăng chưa hỗ trợ.")
    row = state.setdefault("publication_controls", {}).setdefault(ident, {})
    if choice in ("request_delete", "cancel_delete") and row.get("deletion") in ("deleting", "uncertain", "deleted_on_youtube"):
        raise ValueError("Đang/chưa rõ/đã xoá trên nền tảng; không ghi đè trạng thái.")
    if choice in ("hide", "restore"):
        row["hidden"] = choice == "hide"
    elif choice == "bind":
        p = find(state["products"], data["product_id"])
        row.update(product_id=p["id"], affiliate_url=p["affiliate_url"], shop_id=p["shop_id"],
                   item_id=p["item_id"], variant=p["variant"], account=p["account"], platform=p["platform"],
                   placement=p["placement"], binding_method="owner_assigned_not_platform_verified")
    else:
        if choice == "request_delete" and data.get("confirm_id") != ident:
            raise ValueError("Gõ đúng ID video để tạo yêu cầu xoá.")
        row["deletion"] = "requested_not_deleted" if choice == "request_delete" else "cancelled"
    row["updated_at"] = stamp()
    return {"video_id": ident, "choice": choice}
