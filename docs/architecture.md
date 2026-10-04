# Kiến trúc đích và bản đã triển khai

## Bản hiện tại trong repo

Console → control API → adapter gọi đúng runner legacy.
Control API đọc health/queue/báo cáo và lưu lịch sử riêng; adapter chỉ gọi ba ID
trends/media/readiness. Workspace SQLite lưu batch hai nhánh, source/hold/revision,
copy/confirmation. Created adapter gọi công cụ voice/graphics/QC cố định trên host.
URL nguồn chỉ metadata, không trở thành URL tải hoặc lệnh shell. UI chưa có endpoint public.

## Đích sau migration

```mermaid
flowchart TD
  UI[Console: xem, chạy bước, review, pause] --> C[Control API]
  N[n8n: lịch và điều phối] --> C
  C --> Q[(Jobs / revisions / publish ledger)]
  Q --> D[Discover + product match + owned affiliate link]
  D --> SEL[Tìm/đề cử không lọc quyền; chủ chọn nguồn]
  SEL --> E[Chủ xác nhận nguồn; dùng lại xác nhận hợp lệ]
  E --> B[Selected: xử lý chính video nguồn được phép / Flow edit]
  D --> A[Created: script / voice / graphics / scenes tự dựng]
  B --> QC[Decode + nghe/xem + kiểm link/SKU]
  A --> QC
  QC --> R[Review hoặc release policy theo tài khoản]
  R --> P[Publisher theo nền tảng]
  P --> V[Verify processing, vị trí link, URL bài đăng]
  V --> M[Retention / click / commission]
  M --> D
  S[Connection/session service] --> D
  S --> B
  S --> P
```

## Quyền sở hữu theo module

Giữ layout README. Mở rộng có mục tiêu, không tạo service cho mỗi folder:

```text
apps/console/                workspace/source/output/settings views và bảy khu vực
services/control-api/        routes/use-cases/read-models, không nhúng renderer
packages/domain/            two_video/publication contracts; catalog/metrics expansion planned
services/connectors/         OAuth/capabilities/key refs, session metadata (planned)
services/browser-worker/     profile local/Flow adapter/owner handoff (planned)
services/media-worker/       source/edit/timeline/audio/QC (planned)
services/publisher/          account/platform/placement/ledger/reconcile (planned)
orchestration/n8n/           contracts/generator/IDs, không credentials trong export
infra/docker/               Compose/profiles/Dockerfile; không Docker socket vào UI
config/                     schema và cấu hình mẫu, không session/key thật
.agents/skills/              hướng dẫn development/production/connections
```

Source target ≤200 dòng/tệp, hard 250; hàm Python ≤60. SQLite single-host với
migrations/transactions; đa worker mới xét Postgres. Private runtime giữ media,
browser profile/token/DB/log; Git cá nhân chỉ code/config mẫu/docs/skills.

| Module | Sở hữu | Không sở hữu |
|---|---|---|
| console | preview, review, account/topic routing, lịch sử | token, logic render |
| control-api | phiên quản trị, run reserve, quyền thao tác, trạng thái | browser cookies hoặc thuật toán dựng |
| domain | product/media/link/post contracts, transition rules | HTTP, filesystem credentials, Docker |
| n8n | schedule, dependency giữa bước, retry safe reads, gửi ID job | giọng, render, secret trong Code node |
| connectors | OAuth/API capability và refresh; session status | chọn nội dung hoặc tự bật thanh toán |
| browser-worker (phase 3) | local persistent profile, mở login, thao tác UI Flow hợp lệ | export cookie hoặc xoá nguồn của video khác |
| media-worker (phase 4) | created renderer và selected source/Flow edit, voice/captions/QC | publish, sửa link tài khoản |
| publisher (phase 5) | upload reserve, account identity, final URL, reconciliation | tạo nội dung hoặc suy doanh thu |

## Trạng thái và dữ liệu

Job: discovered → product_matched → source_selected → source_confirmed →
link_verified → brief_ready → producing →
qc_ready → review_ready → approved → publishing → published_verified → measured.
Các trạng thái phụ: needs_owner, blocked, failed, interrupted, paused.

Mỗi bước có run_id, batch_id, job_id, revision, input_hash, artifact_sha256,
started_at/completed_at, nguồn bằng chứng và expires_at. Bất kỳ sửa media/copy/
SKU/account/link nào vô hiệu approval cũ. Media đổi tạo revision; copy đổi tăng
copy_version và cần approval mới. Review gắn đúng mã băm và copy_version.
Xác nhận nguồn gắn source/hash/phạm vi/hạn; tìm kiếm/ranking không lọc quyền.
Back chỉ xem; rerun tạo revision và invalidation DAG. Lease/fencing ngăn worker
cũ ghi kết quả vào bản mới; recommended_id không tự ghi đè selected_id.

Publish ledger unique(account_id, platform, job_id, revision). Timeout sau upload
chuyển uncertain và reconcile; không tự gửi lại tệp. Khóa daily batch duy nhất
theo topic/account/local_date; cron không tạo thêm batch khi người dùng click lại.

## Tự động và kiểm soát

Hai chế độ theo account/topic: review (giữ bản sẵn sàng) và auto (tự release khi
đủ điều kiện của cấu hình đã chọn). Owner có thể pause lịch, reject từng revision,
sửa brief rồi tạo revision mới, chạy từng bước, hoặc chạy batch tổng hợp.
Không bắt người dùng review mọi batch nếu đã chọn auto cho account đó.
Mục tiêu mặc định là auto sau khi route nghiệm thu; hold tồn tại sau restart và
được kiểm ngay trước gửi. Warning phong cách không chặn; blocker phải xử lý.
Settings bỏ hỏi lặp bằng xác nhận còn hiệu lực, không bỏ xác nhận nguồn unknown.

Session hết hạn/CAPTCHA, thiếu quyền nguồn, thiếu tín dụng hoặc scope xuất bản
đưa đúng bước vào needs_owner. Các job khác vẫn tiếp tục khi không phụ thuộc.
Một hệ thống có thể vận hành tự động hằng ngày nhưng không thể bảo đảm web Flow
không bao giờ yêu cầu chủ tài khoản đăng nhập/xác minh lại.

## Chuyển đổi không gián đoạn

Legacy→adapter→module mới→shadow run→đối chiếu→chuyển một schedule→ngừng bản cũ.
Console hiện không sửa scheduler live. Tất cả chuyển lịch phải ghi vào deployment
ledger; không chạy song song hai publisher cho cùng publish key.
