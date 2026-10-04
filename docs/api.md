# API của bản quản lý hiện tại

Host mặc định 127.0.0.1:8787. Phiên HttpOnly/SameSite=Strict; POST same-origin +
X-CSRF-Token; API không cấp quyền chạy khi chỉ biết URL. GET / tạo phiên local owner.
Đây là console một người dùng trên máy, không phải hệ thống login đa người từ xa.

| Method | Route | Dữ liệu |
|---|---|---|
| GET | /health | tình trạng service, không đọc tài khoản |
| GET | /api/overview | worker, snapshot tuổi dữ liệu, video, stages, actions |
| GET | /api/runs | tối đa 50 lượt chạy gần nhất |
| POST | /api/actions/{trends,media,readiness} | {"idempotency_key":"uuid hoặc ID tương đương"} |

GET /api/overview trả csrf_token riêng phiên. Không có endpoint nhận path, shell,
credential, cookie hay URL tùy ý. Run POST trả 202/run_id; click lặp cùng key trả
lại run; khác key khi đang chạy trả 409. Media không có job đủ điều kiện trả 412.
Body tối đa 4 KiB. Kết quả runner được chọn trường, stdout/log nằm ngoài Git.

Các contract phase 2–5 sẽ bổ sung dưới /api/v1:

- POST /batches: topic_id, local_date, target_account_ids, mode; reserve unique.
- POST /jobs/{id}/steps/{step}/runs: revision, idempotency_key; dependencies checked.
- POST /jobs/{id}/reviews: revision, sha256, verdict, timecode notes.
- POST /connections/{id}/login và /resume: tương tác owner, không trả secrets.
- POST /schedules/{id}/pause: pause lịch thuộc dự án; không tắt Docker chung.
- GET /publications: platform/account/permalink/link evidence, status.

Những route sau chưa được tạo. Không dùng UI mock để báo chúng đã chạy.
