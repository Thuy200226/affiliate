from datetime import datetime, timezone
from urllib.parse import urlsplit

from .legacy import ACTIONS


def fresh(record, field="checked_at", maximum=3600):
    try:
        stamp = datetime.fromisoformat(record[field])
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        return 0 <= age <= maximum
    except (ValueError, KeyError, TypeError):
        return False


def affiliate_link(bridge):
    jobs = bridge.snapshot("upgrade/local_video_jobs.json").get("jobs", [])
    for job in jobs:
        link = job.get("affiliate_url", "")
        parsed = urlsplit(link)
        if parsed.scheme == "https" and parsed.hostname in ("s.shopee.vn", "shopee.vn"):
            return link
    return None


def summarize(bridge):
    health = bridge.worker("health")
    queue = bridge.worker("jobs/next")
    readiness = bridge.snapshot("artifacts/project-runtime-readiness.json")
    source = bridge.snapshot("artifacts/current-published-videos.json")
    trends = bridge.snapshot("artifacts/live-trends-current.json")
    latest_run = bridge.snapshot("artifacts/rerun-readiness.json")
    failed_api = latest_run.get("ok") is False and latest_run.get("error_type") == "NodeApiError"
    videos = [{key: video.get(key) for key in ("video_id", "privacy_status", "total_platform_views")}
              for video in source.get("videos", []) if video.get("kind") != "technical_test_not_affiliate"]
    actions = []
    for key, (title, _) in ACTIONS.items():
        enabled, reason = bridge.eligible(key)
        actions.append({"key": key, "title": title, "enabled": enabled, "reason": reason})
    return {
        "worker_ok": health.get("ok") is True,
        "queue_job": queue.get("job_id"),
        "observed_at": source.get("checked_at"),
        "snapshot_fresh": fresh(source), "videos": videos,
        "fully_automated": readiness.get("fully_automated_project") is True and fresh(readiness),
        "confirmed_commission": readiness.get("confirmed_affiliate_commission") if fresh(readiness) else None,
        "affiliate_url": affiliate_link(bridge),
        "blockers": readiness.get("blockers", []),
        "trend_count": len(trends.get("candidates", [])) if trends else None,
        "trend_observed_at": trends.get("observed_at"),
        "actions": actions,
        "connections": [
            {"title": "YouTube", "status": "Lượt đọc mới nhất báo lỗi API/kết nối" if failed_api else
             "Có bản ghi tài khoản/video" if videos else "Chưa có bằng chứng"},
            {"title": "Shopee Affiliate", "status": "Có link đã cấu hình; cần đối chiếu mới" if affiliate_link(bridge) else "Chưa cấu hình"},
            {"title": "Google Flow", "status": "Session/quyền nguồn chưa xác nhận mới"},
            {"title": "TikTok / Meta", "status": "Chưa kiểm chứng quyền đăng qua API"},
        ],
    }
