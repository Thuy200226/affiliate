# Workflow hiện hành: một video tự tạo + một video được chọn

Chốt theo hai lời làm rõ mới nhất của chủ ngày 04/10/2026. Tài liệu này thay phạm
vi B-only trước đó; không thay đổi bài đăng hoặc mã băm lịch sử.

## Hai đầu ra độc lập

| Nhánh | Đầu vào | Đầu ra |
|---|---|---|
| created | sản phẩm, kịch bản và lời đọc tự viết | video do hệ thống tự dựng |
| selected | source_id trong danh sách video tìm kiếm | bản xử lý chính nguồn đã chọn, không thay bằng created |

Mỗi nhánh có revision, trạng thái, hold, copy_version, copy/hashtag, run_id,
artifact/hash và lịch sử riêng. Đổi nguồn chỉ làm lại selected; sửa lời/chữ chỉ
làm lại created. Không gộp hai nhánh hoặc giả clip intro là nguồn đã xử lý toàn bộ.
Không tự thay nguồn khi thiếu điều kiện. Chủ xem, sửa, giữ, bỏ giữ và làm lại từng
bản. Revision giữ tối đa 20 bản lịch sử; worker cũ không ghi vào revision/run mới.
Hai cửa sổ sửa cùng version nhận conflict, không âm thầm ghi đè.

## Bảy khu vực quản lý

1. Tổng quan: health, số nguồn/đang dựng/đã dựng, public count, tuổi số liệu, hoa hồng.
2. Tổng hợp: sản phẩm/biến thể/link, danh sách video, chọn nguồn và xác nhận riêng.
3. Đang xử lý: bước thật, lỗi và lý do chưa thể tiếp tục; không timer % giả.
4. Hai video chờ đăng: preview hai nhánh, copy/hashtag, hold/revision/QC.
5. Đã đăng: card permalink, thumbnail/player công khai và public/private từ registry.
6. Kết quả: lọc từng ID bài, thời điểm/metrics; cập nhật kết nối thật, stale/null/error
   không biến thành số 0 hoặc gán hoa hồng tổng vào từng bài.
7. Settings/hướng dẫn: raw query, thứ tự, giới hạn, reuse confirmation, mở kết nối lại.

Tự làm mới không xoá biểu mẫu đang sửa hoặc dừng video đang phát. Nút chưa nối
disabled với lý do. “Đã dựng” không có nghĩa “đã đăng” hoặc “có hoa hồng”.
Preview nguồn YouTube là player nhúng, không là tệp nguồn đã nhận. Preview MP4
hai nhánh chỉ hiện khi có artifact. Preview nội dung đăng có account/copy/tag/link;
Shorts vẫn cần đường hồ sơ nhấp được. Kết quả riêng tư không tự đổi thành công khai.

## Tìm kiếm, chọn và xử lý

Query nguyên văn; search/ranking không lọc theo quyền. URL chuẩn hoá/dedupe theo
sản phẩm. Phân biệt metadata nhập thủ công và provider. Views/hook score chưa đọc
giữ null; tổng views không chứng minh tốc độ tăng hay bắt trend. Không suy công
dụng sản phẩm từ tiêu đề review người khác. “Nhạy cảm” là gây chú ý/tranh luận,
không phải tình dục; hook phải gắn sản phẩm, không bịa trải nghiệm/công dụng.

Chủ xác nhận sau selection. reuse_valid bỏ hỏi lại cùng source/phạm vi/hạn còn
hiệu lực. Xác nhận URL sơ bộ có asset_hash=null, chưa là xác nhận tệp MP4 thực tế.
Đổi nguồn không mang xác nhận sang nguồn khác. Selected cần asset có nguồn rõ,
confirmation, edit request, capability Flow/quota thật và QC trước/sau. Edit người
cần phạm vi đồng ý phù hợp; không giả người thật quảng cáo, không xoá watermark/
nguồn để che lấy lại video. Chữ do chủ tự thêm có thể chỉnh. Không hứa Flow hỗ trợ
mọi video/face-edit. Không nói AI/tự động/thu nhập trên giọng/chữ; metadata nền tảng
cần thiết vẫn giữ. Claim chưa có bằng chứng bỏ khỏi copy, không khẳng định giả.

## Phases và phần đã triển khai

| Phase | Kết quả thực tế | Cổng tiếp theo |
|---|---|---|
| P0 cấu trúc/Git | modules/line limit, private ngoài Git, repo cá nhân | staged scan, hai lượt review |
| P1 workspace | bảy khu vực, hai nhánh, source picker, edit/hold/revision, Range preview | mở rộng catalog/ảnh và lịch sử |
| P2 created | nối giọng/graphics offline M31, preflight/full decode | nghe/xem bản thật, link/SKU mới |
| P3 selected | lưu nguồn/confirmation/edit request; Flow runner chưa nối | MP4 hợp lệ, capability edit thật, QC |
| P4 publisher/link | hợp đồng link có tests, registry legacy đọc được | refresh OAuth, link mới, upload/reconcile hai nhánh |
| P5 daily/metrics | chưa bật lịch tạo/đăng mới, thiếu metrics/commission mới | route đủ quyền, unique/caps, quan sát thực tế ≥7 ngày |

Search API dùng adapter YouTube chính thức nhưng máy chưa cấu hình kết nối này;
mở web và thêm URL dùng được. Không trích cookie giả API. Created chỉ M31 đúng
shop/item vì graphics legacy đặc thù; Swift/voice chạy host Mac, không phải Docker Linux.

## Auto, đăng và nghiệm thu

Auto là mục tiêu mặc định theo topic/account sau nghiệm thu. Warning phong cách
hiện ở quản lý; hold chủ và hard blocker kiểm server trước gửi. Lịch kiểm tra 3h
khác lịch đăng daily. Không bật publisher cũ để lấp khoảng trống. Cash mới=0.
Link/CTA/hashtags phải đúng account/SKU/variant/affiliate owner, gắn media hash và
copy_version. Shorts dùng link hồ sơ đã kiểm nhấp, không URL mô tả/comment giả
clickable. Nền tảng khác cần capability thật. Timeout upload giữ uncertain/reconcile.
Gói đăng tay có MP4/copy/checklist; permalink chủ nhập chưa là published_verified.

Lượt review 1: domain/state/version/race/API/Range/secret/line/module tests. Lượt 2:
UI/restart và renderer/MP4 thật, ghi lỗi/fix/retest. Case chưa có runner/account
không pass từ fixture. Views, retention, organic clicks, đơn chờ, approved commission,
paid amount riêng; không cam kết hoàn hảo, viral hay hoa hồng từ kỹ thuật đạt.
