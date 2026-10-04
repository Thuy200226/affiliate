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

## Vận hành hai video và review

Tạo batch trên console, sửa 5 cảnh created rồi Xử lý. Preview nằm trong Hai video;
video thứ hai chọn từ Tổng hợp, xác nhận bởi chủ và lưu yêu cầu edit riêng.
Đổi nguồn không làm mất created. Giữ/Bỏ giữ riêng từng bản; Làm lại tạo revision.
Database content.sqlite và media nằm .local ngoài Git. Search key qua Settings/
Keychain hoặc AFFILIATE_YOUTUBE_API_KEY, không nhập vào Git hoặc export credential.
Nguồn thêm thủ công chỉ có URL/title chủ nhập; views/hook/creator chưa biết giữ unknown.
Created có đồ hoạ M31 và mẫu trung tính cho sản phẩm khác trên host Mac; selected
nhận MP4 nguồn/đầu ra để preview trước/sau, Flow runner chưa nối. Không có
public publisher mới hoặc daily scheduler. Nút disabled là điều kiện thật chưa đủ.

Danh sách nguồn: mở “Xem preview ngay tại đây” để xem YouTube nhúng, đóng để gỡ
player; thumbnail không có nghĩa đã tải MP4. Nhánh chờ đăng có preview nội dung
account/tiêu đề/mô tả/tag/link riêng. Bài đã đăng có public/private và nút xem kết
quả riêng; bộ lọc thêm ID cho tiêu đề trùng. Bảng cuộn ngang trong khung trên mobile.
“Cập nhật số liệu từ YouTube” gọi readiness hiện có, không xoá số liệu cũ nếu OAuth
lỗi. Kết nối lại ở Settings trước khi thử lại. Chưa có retention/click/commission
theo bài giữ “Chưa có dữ liệu”, không suy hoặc gán từ tổng. Form chưa lưu có hộp
hỏi trong trang: Escape/“Giữ nội dung đang sửa” không mất draft; Tab chuyển hai nút.

Danh mục: chọn nhóm hàng/từ khoá, Làm trước/Bỏ ưu tiên hoặc Bỏ qua/Khôi phục.
Bỏ qua giữ mọi nhánh sản phẩm; khôi phục không tự bỏ giữ. Tạo batch chốt snapshot
Shop/Item/variant/link/account/route; sửa catalog không đổi video lịch sử.
Nguồn nhiều nền tảng được lưu URL; chỉ MP4 nhận/kiểm thực mới có local player.
Upload tối đa 100 MB/180s, giữ hash nguồn/đầu ra riêng; file lỗi không vào hàng chờ.
Settings mỗi tool mở Chrome profile riêng; lần đầu có thể cần login lại, không sao
chép Chrome đã đăng nhập. Key/token không trả lại UI. API scope/login chưa probe
hiện unknown; không gắn key vào Flow rồi gọi API trả phí.
Bài đăng: Ẩn khỏi bảng phục hồi được và không xoá YouTube. Xoá vĩnh viễn là thao tác
riêng có typed ID + OAuth owner, không tự test trên bài thật. Uncertain phải đối chiếu.
Thống kê Shopee: chọn kỳ/phạm vi, nhập từ báo cáo thật; để trống dữ liệu thiếu.
Ước tính/tổng đơn khác duyệt/paid. Account totals không chia cho từng video.
QA UI dùng scripts/qa_console.py (port 8788, fixture cách ly); không đưa fixture
sản phẩm/link vào workspace thật. Xem docs/review-20261004-catalog.md.

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

Đọc [plan hai video](two-video-workflow.md) và [cases](workflow-cases.md). Mỗi batch
created+selected độc lập, không xoá bài lịch sử. Tìm kiếm/ranking không lọc quyền;
chủ chọn rồi xác nhận nguồn. Settings có reuse_valid để bỏ hỏi lặp đúng source/hash/
phạm vi; nguồn unknown vẫn chờ chủ và không tự bị thay bằng video khác.

Back là xem, rerun tạo revision và giải thích impact. Hold của chủ phải tồn tại qua
reload/restart/lượt cron và được kiểm ngay trước gửi. Quota/session/Flow edit không
khả dụng thì giữ đúng bước; không tự biến job thành format khác hoặc bật API phí.

Lịch tạo/đăng daily khác lịch kiểm tra 3h. Trước cutover: backup+restore, reconciliation,
route/link identity, hai lượt review, thử restart/race và toàn bộ B nghe/xem thật.
Chỉ sửa lịch thuộc dự án; không dừng/xóa Docker dự án khác hoặc chạy hai publisher.
