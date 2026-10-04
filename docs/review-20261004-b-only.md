# Hai lượt review — yêu cầu B-only, 04/10/2026

Đối tượng: repo nền tảng mới và phần runtime legacy liên quan. Lượt này chốt thiết kế,
không triển khai bảy màn hình, đổi lịch, tạo video, đăng bài hoặc nối lại OAuth.
Thời điểm kiểm tra dịch vụ/UI và validators bổ sung: khoảng 13:05 giờ Việt Nam.
Không phải audit độc lập toàn diện về bảo mật, dependency hoặc mọi case nghiệp vụ.

## Lượt 1 — mã, hợp đồng và kiểm thử nền tảng

Đọc kiến trúc/API, module domain/control, skills và plan cũ; đối chiếu toàn bộ yêu
cầu với matrix hiện hành. Kiểm invariant source/selection, revision/link/account,
backtracking, publish idempotency, giới hạn file/hàm và dữ liệu không được vào Git.

| Kiểm tra thực sự đã chạy | Kết quả | Phạm vi chứng minh |
|---|---|---|
| scripts/check_repo.py | đạt | pattern secret/artifact, code ≤250 dòng, Python function ≤60; không phải full secret audit |
| scripts/test.py | 18 tests đạt | session/CSRF/host/API/body/path; reserve/concurrency/restart; owner/SKU/variant/account/TTL/link placement |
| node --check apps/console/app.js | đạt | cú pháp JS, không chứng minh mọi hành vi UI |
| quick_validate affiliate-development/affiliate-production | đạt | cấu trúc hai project skills đã sửa, không cài skill toàn máy |

Đã sửa trong tài liệu: scope future chỉ B; đề cử không lọc quyền; xác nhận sau
selection do chủ; Settings reuse_valid theo đúng source/hash/phạm vi; ranh giới
warning/blocker/auto/hold; back chỉ xem, rerun tạo revision; đầy đủ 7 khu vực,
API dự kiến, phase/acceptance, hai lượt review. Plan A/B cũ được đánh dấu lịch sử.

## Lượt 2 — dịch vụ, UI đang chạy và validators legacy

Kiểm tra read-only, không gọi upload/public release hoặc tạo click affiliate.

| Kiểm tra thực sự đã chạy | Kết quả | Không được suy ra |
|---|---|---|
| Docker inventory | affiliate-n8n đang chạy | không thay đổi stack/Docker các dự án khác |
| GET console :8787/health | ok, affiliate-control | không chứng minh login xã hội hoặc publisher mới |
| GET worker :6789/health | ok; public_publish_allowed=false; paid_AI_API_calls=0 | không chứng minh B hằng ngày đã chạy |
| Compose config --quiet, giá trị key giả chỉ để parse | exit 0 | chưa build/run stack mới hoặc renderer Linux |
| UI tab :8787/#formats | worker khả dụng; queue chưa có bản đủ điều kiện; lịch sử lỗi được giữ | UI vẫn là bản nền tảng A/B, không phải 7 khu vực B-only |
| unittest test_full_flow_story | đạt | manifest với fixture; không tạo/nghe/xem B mới |
| unittest test_content_requirements | đạt | guard intro legacy; vẫn chấp nhận graphics_clean cho future — chưa đúng B-only |

UI hiện 3 bài public, tổng snapshot 312 lượt xem tại 17:00:49 ngày 03/10, ghi rõ
cần làm mới; hoa hồng xác nhận “chưa biết”. Không gọi đó là số liệu live 04/10.
Readiness ở lịch sử 11:38 ngày 04/10 thất bại tại YouTube; trend lúc 11:42 thành
công. Chưa có thay đổi OAuth nên không lặp một lần đọc sẽ mắc cùng điều kiện.

## Phát hiện và cổng đóng

| ID | Mức | Phát hiện có bằng chứng | Hướng đóng/cổng kiểm tra | Trạng thái |
|---|---|---|---|---|
| B01 | P1 | apps/console vẫn có A/B; test_content_requirements vẫn cho graphics_clean future | migrate B-only routes/guards, giữ immutable bài cũ; W01 + UI | còn mở, không sửa runtime live ở lượt plan |
| B02 | P1 | full_flow_story là bộ dựng độc lập; local_video_worker không gọi nó | nối job contract/queue/adapter, B xuyên suốt và toàn MP4 QC; W18–W24 | còn mở |
| B03 | P1 | live_trend_collector là RSS và hardcoded keyword allowlist, không là source-video collector/profile chủ | collector đúng capability, raw queries/version/source list + picker; W02–W10/W51 | còn mở |
| B04 | P1 | source confirmation/settings/reuse_valid chưa có API/UI; face-edit chưa có runner/capability evidence | chủ xác nhận sau selection; refs/hash/scope/expiry, spike asset được phép, before/after QC; W07/W18–W20/W52–W53 | còn mở |
| B05 | P1 | khóa console chưa thống nhất với lịch legacy; chưa có publisher B/hold/fencing chung | transaction/ledger/reconcile/cutover một chủ lịch; W09/W14–W15/W27–W31/W48 | còn mở |
| B06 | P1 | latest readiness lỗi YouTube auth; metrics/Shopee/commission mới chưa có | chủ khôi phục kết nối đúng scope khi sẵn sàng; readback/coverage/attribution; W32–W44 | còn mở, dữ liệu mới chưa biết |
| B07 | P2 | console chưa autostart qua reboot, Docker mới chưa chạy, worker phụ thuộc Mac | service/restore/cutover test; W47–W49, portable renderer chỉ sau kiểm chứng | còn mở |
| B08 | P2 | tài liệu active còn mục tiêu A/B, thiếu mapping yêu cầu mới | sửa plan/architecture/API/operations/n8n/skills, banner lịch sử | đã sửa trong đặc tả; không coi code đã migrate |

## Nghiệm thu còn phải thực hiện

[53 ca workflow](workflow-cases.md) là test backlog, **không phải 53 tests đã đạt**.
Hai lượt này chỉ đánh giá nền tảng và khoảng cách triển khai; chưa có E2E B/face-edit,
UI mobile/keyboard mới, source picker/hold/revision API, remote publish/readback,
fresh Analytics/Shopee, restore/cutover hoặc quan sát daily 7 ngày.

Phải có evidence và fix→retest ở mỗi phase. Unit pass không chứng nhận chất lượng
cảm nhận, tương tác hay hoa hồng. Chỉ kết luận doanh thu khi có báo cáo hoa hồng
được duyệt; không hứa “hoàn hảo”, hết mọi lỗi hoặc chắc chắn mang lại hoa hồng.
