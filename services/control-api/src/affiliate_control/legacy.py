"""Only the already-deployed runner and fixed local worker endpoints."""
import json
import subprocess
import sys
from urllib.request import urlopen


ACTIONS = {
    "trends": ("Làm mới trend", "9e14f52bf2202829"),
    "media": ("Chạy hàng đợi video", "04868d9653749779"),
    "readiness": ("Kiểm tra hệ thống", "3c40800415102804"),
}


class Legacy:
    def __init__(self, settings):
        self.settings = settings

    def snapshot(self, relative):
        if self.settings.runtime is None:
            return {}
        path = self.settings.runtime / relative
        try:
            if not path.is_file() or path.stat().st_size > 2_000_000:
                return {}
            data = json.loads(path.read_text())
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def worker(self, route):
        if route not in ("health", "jobs/next", "uploads/pending") or self.settings.runtime is None:
            return {}
        try:
            with urlopen("http://127.0.0.1:6789/" + route, timeout=3) as response:
                data = json.loads(response.read(65536))
                return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def eligible(self, flow):
        if flow not in ACTIONS:
            return False, "Luồng chưa được triển khai trong bản quản lý."
        if self.settings.runtime is None or self.worker("health").get("ok") is not True:
            return False, "Chưa nối runtime hoặc worker chưa khả dụng."
        if flow == "media" and self.worker("jobs/next").get("job_id") is None:
            return False, "Hàng đợi chưa có video đủ điều kiện."
        return True, ""

    def execute(self, flow, ident):
        if flow not in ACTIONS or self.settings.runtime is None:
            raise ValueError("Action not configured")
        command = [sys.executable, str(self.settings.runtime / "upgrade/run_existing_affiliate_flow.py"), flow]
        result = subprocess.run(command, cwd=self.settings.runtime, capture_output=True,
                                text=True, timeout=700, shell=False)
        log = self.settings.state / "logs" / (ident + ".log")
        log.write_text((result.stdout + result.stderr)[-2_000_000:])
        try:
            report = json.loads(result.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return "failed", {"message": "Không đọc được kết quả; xem log cục bộ."}
        ok = result.returncode == 0 and report.get("ok") is True
        details = {
            "ok": ok, "workflow_id": ACTIONS[flow][1],
            "upload_node_executed": report.get("upload_node_executed") is True,
            "public_posts": report.get("public_posts"),
            "paid_AI_API_calls": report.get("paid_AI_API_calls"),
        }
        if not ok:
            details["error_type"] = report.get("error_type")
            details["message"] = "Workflow báo lỗi; kiểm tra kết nối tài khoản và log cục bộ."
        return ("succeeded" if ok else "failed"), details
