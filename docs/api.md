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

## Bổ sung cho console sản phẩm — planned

Các contract sau thuộc P1–P4 của plan B-only, không phải route hiện có:

| Route | Trách nhiệm |
|---|---|
| GET /api/v1/products và /products/{id} | catalog/variants/evidence, lọc topic/account/status |
| GET /api/v1/publications và /publications/{id} | registry; product/account/visibility, URL/readback |
| GET /api/v1/metrics | object/metric/kỳ/nguồn/coverage; không trả token hay dữ liệu người mua |
| POST /api/v1/metric-syncs | reserve sync theo connection/kỳ; trả run_id, không đồng bộ chặn UI |
| GET /api/v1/discoveries | nguồn/tín hiệu, age/relevance/SKU match, lý do gợi ý |
| GET /api/v1/jobs và /jobs/{id} | hàng chờ/revision/QC/checklist và bước hiện tại |
| GET /api/v1/artifacts/{id}/preview | media allowlist của job; hỗ trợ Range, không nhận path |
| POST /api/v1/jobs/{id}/revisions | tạo bản sửa; expected_revision để chống ghi đè |
| POST /api/v1/publication-requests | job/revision/approval/route/idempotency_key; server đọc payload đã chốt |
| GET /api/v1/publication-requests/{id} | tiến độ/uncertain/reconcile và URL đã xác minh |
| POST /api/v1/manual-publication-reports | permalink chủ khai báo, cần kiểm tra account/media trước xác minh |
| GET /api/v1/schedules | lịch/topic/account/mode/caps; lịch kiểm tra khác lịch đăng |

## Selection, xác nhận nguồn và Settings — planned

| Route | Trách nhiệm |
|---|---|
| GET /api/v1/search-profiles/{id} | raw queries/prompts/criteria, version và provider capability |
| POST /api/v1/search-profiles/{id}/versions | expected_version, raw query của chủ; batch cũ giữ snapshot |
| POST /api/v1/discovery-runs | profile_version/product/topic/idempotency; không lọc quyền khi tìm/rank |
| GET /api/v1/discovery-runs/{id}/videos | mọi kết quả connector, metrics/source/time, recommended khác selected |
| POST /api/v1/jobs/{id}/source-selections | source_id/expected_revision; đổi nguồn tạo revision và impact preview |
| POST /api/v1/source-confirmations | owner xác nhận source/hash/phạm vi/hạn; không tự suy từ search |
| POST /api/v1/source-confirmation-settings/versions | per_source hoặc reuse_valid; không bỏ kiểm unknown |
| POST /api/v1/jobs/{id}/edit-requests | revision/timecodes/character_ref/request; capability và consent kiểm ở xử lý |
| POST /api/v1/jobs/{id}/rerun-plans | chỉ preview DAG/quota/invalidation; chưa gọi render hoặc publish |
| POST /api/v1/jobs/{id}/revisions/{revision}/next | dependencies/lease/fencing; trả run hoặc reason, không chỉ đổi badge |
| POST /api/v1/jobs/{id}/holds | expected_revision/reason; durable hold dùng chung manual/auto |
| DELETE /api/v1/jobs/{id}/holds/{hold_id} | owner bỏ hold đúng revision; không tự publish chỉ vì bỏ hold |
| GET /api/v1/jobs/{id}/timeline | progress thật, heartbeat, timecodes/artifacts, lỗi/next_action |
| GET /api/v1/jobs/{id}/comparisons | nguồn/B/revisions, copy/link binding; không có nhánh A future |

Confirmations bất biến hoặc revoked; tái dùng chỉ đúng source/hash/scope còn hiệu lực.
Thông tin quyền thiếu không làm mất kết quả tìm kiếm hay tự thay nguồn đã chọn.
Edit chưa được capability xác nhận trả needs_owner/blocked; không báo face-edit xong.
Hold/revision được đọc trong transaction ngay trước gửi; đã gửi thì reconcile.

Server trả reason_codes/checklist và next_action cho bước blocked; không trả một
boolean “ready” thiếu lý do. Mutations kiểm session/CSRF/revision và quyền đích.
Public request thiếu điều kiện trả 412; conflict/race trả 409; 202 chỉ là đã nhận
job, không phải đã đăng. Upload uncertain giữ reservation để đối chiếu, không retry mù.

Xem [console B-only/đăng tay](b-only-console-plan.md) và [metric contracts](metrics-contract.md).
