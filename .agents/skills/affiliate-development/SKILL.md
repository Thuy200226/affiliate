---
name: affiliate-development
description: Phát triển hoặc refactor module của repository Affiliate Platform; dùng khi sửa API, console, domain, Docker hoặc n8n orchestration.
---

Đọc AGENTS.md và docs/architecture.md. Chọn ranh giới module trước khi sửa:
domain chứa hợp đồng, control API điều phối run, console hiển thị, n8n chỉ lịch/HTTP.
Đọc docs/phases.md khi thay đổi phạm vi hoặc nghiệm thu giai đoạn.

Legacy ở runtime ngoài repo. Không chuyển private/artifacts/credential exports
vào source. Không chỉnh job đã đăng; tạo revision mới khi media/copy/link đổi.

Giữ tệp mã ≤250 dòng, hàm ≤60 dòng; tách theo trách nhiệm chứ không cắt tùy tiện.
Chạy scripts/check_repo.py và scripts/test.py sau thay đổi ảnh hưởng hành vi.
Kiểm tra dựa trên request/restart/idempotency/contract, không so khớp wording.

Chuyển module theo adapter → fixture sạch → shadow check → cutover một schedule.
Không activate/import publisher legacy để thử một refactor.
Đọc docs/code-review.md để ưu tiên lỗi đã có bằng chứng.

Yêu cầu hiện hành ở docs/two-video-workflow.md và requirements-matrix.md; B-only
cũ chỉ lịch sử. Khi thêm transition/Settings/source picker/publisher, dùng ma trận
workflow-cases.md và review hai lượt; không ghi planned API/UI là đã vận hành.

Mở rộng nhiều sản phẩm hiện có ở catalog/source_links, catalog_commands,
report_commands, uploads và connections. Đọc docs/review-20261004-catalog.md
khi sửa những đường này; test UI fixture bằng scripts/qa_console.py, không seed
sản phẩm/link giả vào workspace thật. Catalog đổi không sửa batch lịch sử.
