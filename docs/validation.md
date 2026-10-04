# Bằng chứng kiểm tra — 04/10/2026

Lượt hiện hành: [hai lượt review triển khai và UI](review-20261004-two-video.md).
Plan B-only là lịch sử. Các kết quả dưới đây không phải nghiệm thu toàn bộ cases,
Flow selected, daily/publisher hoặc chất lượng cảm nhận và hoa hồng.

## Bộ mã mới

- 44 kiểm thử hành vi đạt: phiên/CSRF/host; API; reserve/restart; binding SKU/variant/
  owner/account; TTL; vị trí link cho Shorts; hai nhánh/conflict/fencing; preflight;
  source URL; MP4 Range/containment/disconnect; console metric null/0; lỗi OAuth
  giữ số liệu cũ và không gán hoa hồng tổng vào bài.
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

Đã dựng created MP4 thật 20.58 giây; preview tải đúng và không báo lỗi. Ba thumbnail
nguồn và player nguồn/bài công khai tải được. Lọc kết quả theo ID, 8 bài đúng trạng
thái public/private; mobile không tràn ngang. Dialog không làm mất draft khi huỷ.
Selected chưa nhận MP4 và chưa chạy Flow; không có bản đăng mới. Hai lượt UI trên
trang thật và chi tiết lỗi/fix/retest ở báo cáo mới phía trên.

Phiên/token/account logs và run database chỉ lưu ngoài Git. Trang đã được giữ mở
cho chủ sử dụng. Muốn duy trì qua reboot cần cấu hình service ở phase triển khai.
