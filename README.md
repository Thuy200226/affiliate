# Affiliate Platform

Bộ mã sạch để chuyển dần hệ thống affiliate hiện có sang các module dễ quản lý.
Ngày đánh giá: 04/10/2026. Giai đoạn hiện tại: nền tảng quản lý và cầu nối legacy.

## Chạy trang quản lý

Yêu cầu Python ≥3.12. Không cần cài thư viện cho bản quản lý cục bộ.

```sh
python3 scripts/dev.py --runtime-root /absolute/path/to/affiliate-automation
```

Mở http://127.0.0.1:8787. Có nút làm mới trend, kiểm tra hệ thống,
chạy hàng đợi media đủ điều kiện và xem lịch sử. Media của runtime hiện tại tải riêng tư.
Các bước chưa triển khai được hiển thị rõ, không có nút giả báo thành công.

Trang này đọc các báo cáo đã có và gọi runner cho phép; không nhập lại workflow,
không sao chép tài khoản. Nếu không truyền runtime, trang chạy ở chế độ chưa kết nối.
Trạng thái/lịch sử/khóa phiên của trang nằm trong .local/, ngoài Git.

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

Kế hoạch mở rộng theo yêu cầu mới: [sản phẩm, tương tác, hàng chờ và đăng tay](docs/product-console-plan.md).
[Hợp đồng số liệu](docs/metrics-contract.md) quy định nguồn, kỳ đo và attribution.
Đây là đặc tả tiếp theo; các màn hình/nút đăng mới chưa được triển khai.

## Mức hoàn thiện

Đã có bộ quản lý cục bộ và adapter cho ba workflow hiện có. Chưa có dịch vụ
đăng nhập xã hội mới, runner Flow không người trực, tự tạo hai video mỗi ngày,
hoặc tự công khai đa nền tảng. Các phần này có điều kiện nghiệm thu riêng trong kế hoạch.
