# Affiliate Platform

Bộ mã sạch để chuyển dần hệ thống affiliate hiện có sang các module dễ quản lý.
Ngày đánh giá: 04/10/2026. Giai đoạn hiện tại: nền tảng quản lý và cầu nối legacy.

## Chạy trang quản lý

Yêu cầu Python ≥3.12. Không cần cài thư viện cho bản quản lý cục bộ.

```sh
python3 scripts/dev.py --runtime-root /absolute/path/to/affiliate-automation
```

Mở http://127.0.0.1:8787. Có chín khu vực quản lý, batch gồm một video tự tạo và
một video chọn từ danh sách; sửa kịch bản/copy/hashtag, giữ/làm lại từng bản, preview
MP4 và lịch sử. Có nút gọi ba workflow legacy; media legacy tải riêng tư.
Các bước chưa triển khai được hiển thị rõ, không có nút giả báo thành công.
Video nguồn và bài công khai có thumbnail/player nhúng; nội dung chờ đăng có preview
account/copy/tag/link. Kết quả lọc từng ID bài, giữ thời điểm và dữ liệu chưa biết.

Trang này đọc các báo cáo đã có và gọi runner cho phép; không nhập lại workflow,
không sao chép tài khoản. Nếu không truyền runtime, trang chạy ở chế độ chưa kết nối.
Trạng thái/lịch sử/khóa phiên và media của trang nằm trong .local/, ngoài Git.

## Bố trí

```text
apps/console/                         giao diện quản lý
services/control-api/src/             API, phiên quản lý, lịch sử thực thi
packages/domain/src/affiliate_domain/ hợp đồng sản phẩm/media/link
orchestration/n8n/                    danh mục luồng và ranh giới điều phối
infra/docker/                        Dockerfile/Compose cho môi trường mới
config/                              ví dụ cấu hình không chứa tài khoản
docs/                                đánh giá, kiến trúc, API, kế hoạch phase
.agents/skills/                      hướng dẫn phát triển và vận hành
tests/                               kiểm thử hành vi
scripts/                             chạy cục bộ, kiểm tra trước Git
```

## Kiểm tra trước Git

```sh
python3 scripts/check_repo.py
python3 scripts/test.py
```

Không commit runtime cũ, bản sao lưu, credential export hay thư mục trình duyệt.
Repository đã push lên `Thuy200226/affiliate`, dùng danh tính cá nhân riêng cho repo.
Xem [kế hoạch](docs/phases.md), [đánh giá code](docs/code-review.md),
[kiến trúc](docs/architecture.md), [cách vận hành](docs/operations.md).

Kế hoạch hiện hành: [hai nhánh video và console bảy khu vực](docs/two-video-workflow.md).
[Đối chiếu yêu cầu](docs/requirements-matrix.md) và [ma trận ca kiểm thử](docs/workflow-cases.md)
phân biệt chức năng cần làm với bằng chứng đã thực hiện. Plan B-only cũ đã bị thay thế.
[Hợp đồng số liệu](docs/metrics-contract.md) quy định nguồn, kỳ đo và attribution.
Workspace/preview/renderer created đã nối; publisher mới và lịch daily chưa nối.
Xem [hai lượt review triển khai](docs/review-20261004-two-video.md); tests console
đạt không có nghĩa Flow/publisher daily hoặc kết quả kinh doanh đã hoàn thành.

## Mức hoàn thiện

Created dùng giọng offline trên Mac; M31 có đồ hoạ riêng, sản phẩm khác dùng mẫu
trung tính đã thử render, không lấy hình M31 cho SKU khác. Danh mục hỗ trợ nhiều
nhóm hàng, query/SKU/biến thể/link/tài khoản riêng; làm trước/bỏ qua/khôi phục.
Search YouTube nhận key từ Keychain hoặc AFFILIATE_YOUTUBE_API_KEY; key không vào Git.
URL TikTok/Instagram/Facebook/nguồn web khác lưu được; URL không có nghĩa đã tải video.
Nhận MP4 nguồn và MP4 đầu ra có kiểm giải mã, hash và preview trước/sau theo ID.
Flow/đổi mặt tự động chưa nối; bản tải vào không tự coi là đã đổi mặt.
Settings có chín công cụ, mở Chrome với hồ sơ riêng và lưu key/token ở Keychain Mac.
Lưu key không chứng minh scope/OAuth hoặc tự nối publisher. Xoá YouTube kiểm chủ sở
hữu và ID, không tự thử lại kết quả chưa rõ; chưa xoá bài thật để kiểm thử.
Shopee có báo cáo theo kỳ/phạm vi, giữ riêng ước tính/chờ/duyệt/đã trả; chưa có
connector tự đọc Shopee. OAuth YouTube legacy đang cần refresh; publisher/daily/
đa nền tảng chưa nghiệm thu. Xem [mở rộng và hai lượt review](docs/review-20261004-catalog.md).
