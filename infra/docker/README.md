# Docker và dịch vụ máy chủ

Compose là môi trường mới, tách khỏi container/volume đang chạy; chưa được khởi động.
Chạy console trên host bằng scripts/dev.py để nối runner legacy hiện có.
Container control hiện chạy chưa kết nối, không mount Docker socket hoặc profile.
Swift/AVFoundation và giọng cục bộ đang phụ thuộc macOS; không hứa chạy trên Linux.

Profile orchestration dùng cổng 5679 và volume mới. Chỉ bật trong phase 2 migration.
N8N_ENCRYPTION_KEY phải lưu ở tệp .env riêng, ngoài Git; không dùng khóa demo.
Tag/digest n8n kế thừa bản đã chạy; xem xét nâng phiên bản bằng staging sau refactor.
Ảnh Python cần ghim digest đã kiểm tra khi chuẩn bị release có thể tái lập.

Môi trường từ xa cần HTTPS, đăng nhập quản trị riêng, backup/restore và quyền dịch vụ.
Phiên loopback của console hiện tại không thay cho tài khoản quản trị từ xa.
