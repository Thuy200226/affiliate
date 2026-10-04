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

## Chuẩn review video B

Xem toàn bộ MP4 và nghe cả âm thanh, không chỉ ảnh đầu/cuối. Ghi timecode cho
hook chậm, giọng sai, phụ đề lệch, khung sản phẩm sai, cảnh đứt hoặc CTA không rõ.
Approval gắn sha256 + revision + account + platform + link, không gắn tên tệp.
Nếu sửa bất kỳ thành phần nào, review bản mới trước release.
QC là bước hệ thống bắt buộc; owner review và auto là hai mode. Auto chỉ bật sau
nghiệm thu route, không bắt chủ click duyệt mọi job đã đủ điều kiện.

Nội dung hút bằng vấn đề cụ thể, hình ảnh nhất quán và giải đáp nhanh. Hashtag lấy
từ chủ đề/sản phẩm đã kiểm chứng. Số view là tổng; retention/click/commission là
dữ liệu riêng, không quy đổi view sang doanh thu.

## Phần vận hành đích chưa triển khai

Đọc [plan B-only](b-only-console-plan.md) và [cases](workflow-cases.md). Không tạo A
cho batch tương lai, không xoá bài A lịch sử. Tìm kiếm/ranking không lọc quyền;
chủ chọn rồi xác nhận nguồn. Settings có reuse_valid để bỏ hỏi lặp đúng source/hash/
phạm vi; nguồn unknown vẫn chờ chủ và không tự bị thay bằng video khác.

Back là xem, rerun tạo revision và giải thích impact. Hold của chủ phải tồn tại qua
reload/restart/lượt cron và được kiểm ngay trước gửi. Quota/session/Flow edit không
khả dụng thì giữ đúng bước; không tự biến job thành format khác hoặc bật API phí.

Lịch tạo/đăng daily khác lịch kiểm tra 3h. Trước cutover: backup+restore, reconciliation,
route/link identity, hai lượt review, thử restart/race và toàn bộ B nghe/xem thật.
Chỉ sửa lịch thuộc dự án; không dừng/xóa Docker dự án khác hoặc chạy hai publisher.
