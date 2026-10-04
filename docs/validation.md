# Bằng chứng kiểm tra — 04/10/2026

## Bộ mã mới

- 18 kiểm thử hành vi đạt: phiên/CSRF/host; API; reserve/restart; binding SKU/variant/
  owner/account; TTL; vị trí link cho Shorts; hạn chế body/path/action.
- Tất cả module mới dưới 250 dòng; hàm Python dưới 60 dòng.
- JavaScript syntax check và Docker Compose config parse đạt; chưa build/chạy stack
  Docker mới hoặc chứng nhận renderer chạy trên Linux.
- Ba project skills qua validator của skill-creator. Không thay skill toàn máy.
- Scanner nguồn/staged files không thấy mẫu secret đã định nghĩa hoặc artifact
  bị cấm. Đây không phải kết luận audit đầy đủ mọi secret có thể tồn tại.

## Thử trang quản lý với runtime thật

Đã mở trang loopback bằng trình duyệt và click hai nút:

| Lượt | Workflow | Kết quả |
|---|---|---|
| Kiểm tra hệ thống | 3c40800415102804 | lỗi API/xác thực YouTube; đã lưu trạng thái thất bại |
| Làm mới trend | 9e14f52bf2202829 | thành công; không gọi upload/publish/AI trả phí |

Đã khởi động lại console: lịch sử thất bại vẫn hiện, phiên được giữ theo khóa riêng.
Media disabled vì hàng đợi trống. Không tạo bản đăng công khai để thử nút.
UI hiển thị 3 video công khai, 312 tổng views theo snapshot 03/10, hoa hồng chưa biết;
snapshot được ghi rõ là cần làm mới, không coi lỗi OAuth là views bằng 0.

Phiên/token/account logs và run database chỉ lưu ngoài Git. Trang đã được giữ mở
cho chủ sử dụng. Muốn duy trì qua reboot cần cấu hình service ở phase triển khai.
