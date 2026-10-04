---
name: affiliate-connections
description: Triển khai hoặc kiểm tra kết nối tài khoản, OAuth, phiên web Flow và capability xuất bản trong Affiliate Platform.
---

Đọc docs/connections.md và docs/api.md. Tách đăng nhập, identity và capability.
Không coi login web/Shopee social linkage là quyền API publish.

DB chỉ lưu credential/profile reference và trạng thái; token ở encrypted store
hoặc keychain, web profile cục bộ ngoài Git. Không export cookie/session vào API/log.
Login OAuth cần state/identity check; profile Flow có lock và trạng thái needs_owner.

Dùng tài khoản đã được chủ giao; kiểm quota/credit hiện tại trước thao tác tạo.
Ngân sách tiền mới hiện là 0. Session/CAPTCHA/terms cần tương tác chủ theo bước
thực tế; không lặp thông báo nếu cùng bước vẫn chờ và không có thay đổi.

Kiểm connector bằng account identity + scope + hành động có thể làm. Báo khả năng
chưa chứng minh là unknown. Sau auth, tiếp tục job từ bước bị chặn thay vì tạo batch mới.
