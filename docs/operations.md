# Vận hành bản quản lý

Chạy scripts/dev.py trên Mac với --runtime-root đúng thư mục runtime.
Mở 127.0.0.1:8787, nhấn Kiểm tra hệ thống và xem lịch sử kết thúc.
Trends làm mới nguồn; Media chỉ gọi khi worker có job. Mỗi nút gửi một run key.
Các lịch legacy vẫn vận hành riêng; console không sửa chúng.

Service mới không autostart sau reboot trong phase 1. Muốn dùng thường xuyên,
thiết lập LaunchAgent/service trong phase cutover sau khi chọn cấu hình/port.
Chế độ Docker hiện là độc lập/chưa nối; không mount Docker socket để chạy legacy.

Nếu một lượt bị ngắt lúc server restart, trạng thái là interrupted. Không tự chạy
lại vì không biết side effect của lượt cũ; đối chiếu ledger/báo cáo trước khi thử.
Logs và database nằm .local/ và được ignore. Không gửi chúng lên Git để debug.

Mã legacy ở thư mục runtime không bị thay đổi bởi việc tạo repo này.
Không di chuyển/xóa volume, session hoặc các publisher trong quá trình review.

## Chuẩn review video

Xem toàn bộ MP4 và nghe cả âm thanh, không chỉ ảnh đầu/cuối. Ghi timecode cho
hook chậm, giọng sai, phụ đề lệch, khung sản phẩm sai, cảnh đứt hoặc CTA không rõ.
Approval gắn sha256 + revision + account + platform + link, không gắn tên tệp.
Nếu sửa bất kỳ thành phần nào, review bản mới trước release.

Nội dung hút bằng vấn đề cụ thể, hình ảnh nhất quán và giải đáp nhanh. Hashtag lấy
từ chủ đề/sản phẩm đã kiểm chứng. Số view là tổng; retention/click/commission là
dữ liệu riêng, không quy đổi view sang doanh thu.
