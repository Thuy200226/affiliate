# Hai lượt review triển khai và giao diện — 04/10/2026

Phạm vi hiện hành: một `created` tự dựng + một `selected` từ nguồn được chọn.
Thay plan B-only; không sửa bài/hash lịch sử. Hai lượt kiểm tra khác phương pháp,
không phải chứng nhận mọi case, mọi nền tảng hoặc kết quả kinh doanh.

## Lượt 1 — hợp đồng, lỗi và hành vi

44 kiểm thử đạt: nền tảng phiên/CSRF/host, domain hai nhánh, copy/source invalidation,
idempotency/restart/conflict/fencing, renderer preflight, media Range/containment,
source URL, metric null/0 và giữ snapshot khi OAuth lỗi. Node kiểm hợp đồng console
được gọi từ suite khi có Node; môi trường lượt này có Node và đã chạy.

| Vấn đề phát hiện | Sửa và kiểm lại |
|---|---|
| Chữ 3 cảnh quá dài làm renderer từ chối | Chia dòng; dựng lại thành MP4 thật, decode đủ |
| Poll có thể xoá form đang sửa hoặc dừng preview | Chặn redraw khi dirty/focus/video đang phát/source iframe mở |
| Lưu một form có thể làm mất form khác | Theo dõi dirty từng form; hỏi bỏ nội dung khác, lỗi vẫn giữ input |
| Hộp confirm native gây kẹt kiểm thử | Dialog trong trang, cancel/Escape, vòng Tab, inert nền và trả focus |
| Client đóng preview tạo BrokenPipe log | Xử lý disconnect bình thường, thêm kiểm thử |
| Bước selected chỉ hiện một blocker | Hiện cả thiếu xác nhận và thiếu runner Flow, không báo thành công giả |
| Tiêu đề bài trùng nhau | Card/table có ID; option bộ lọc thêm ID |
| Thiếu preview và kết quả từng bài | Module preview/source/post + bảng lọc theo ID, giữ null và thời điểm |

Scanner nguồn: 71 tệp nguồn đạt cổng giới hạn/secret/artifact. Tệp mã ≤250 dòng, hàm
Python ≤60; không suy regex thành audit mọi secret. JS syntax và Compose parse
đạt; chưa build/chạy stack Docker mới hoặc chứng nhận renderer Linux. Skills dự
án hợp lệ. Gate staged được chạy riêng trước commit.

## Lượt 2 — UI thật, reload và media

Đã kiểm trên console loopback với runtime hiện có, rồi reload kiểm lại sau sửa:

- Ba thumbnail nguồn YouTube tải được (naturalWidth 480). Nguồn được chọn mở
  trình phát nhúng có nút Play; không autoplay. Đóng preview gỡ iframe.
- Bài công khai `uMAWQBq5u7k` mở trình phát trong card; card riêng tư không nhúng
  công khai, hướng về tài khoản chủ. Không thay quyền hiển thị của bài đăng.
- Nút “Xem kết quả bài này” lọc đúng một dòng ID trên; snapshot 240 views lúc
  17:00:49 ngày 03/10. Chọn tất cả trả 8 dòng, gồm 3 công khai và 5 riêng tư.
- Các ô likes/comments/retention/click/commission chưa có dữ liệu không là 0.
  Lỗi OAuth được hiển thị cùng số liệu cũ; không gọi lại đọc lỗi để giả dữ liệu mới.
- MP4 created có readyState=4, duration=20.583333, 1080×1920, error=null. Nội dung
  chờ đăng hiển thị đúng account/title/description/hashtags/link đã cấu hình.
- Kiểm form chưa lưu: Tab chuyển hai nút, Escape giữ input và mở lại nền; bỏ bản
  chưa lưu khôi phục tiêu đề đã lưu. Không lưu payload kiểm thử hoặc đăng bài.
- Desktop 1280×1000: body 16px, cards/preview/bảng riêng. Mobile 390×844: card
  331px, video 290px; document width 375 ≤ viewport 390. Bảng 1150px cuộn trong
  khung 331px, không đẩy toàn trang tràn ngang. Viewport tạm được reset.

Ảnh kiểm chứng ở thư mục outputs ngoài Git. Font, khoảng cách, nút ≥44px,
focus ring, trạng thái khoá và card nguồn/bản dựng/bài đăng đã được cải thiện.
Đây không phải audit accessibility trên mọi trình đọc màn hình hoặc mọi thiết bị.

## Artifact thật và phần chưa đủ

Created revision 2: 20.58 giây, 1080×1920/24fps, decode 494 khung; âm thanh
48kHz stereo, peak −1.38 dBFS, RMS −17.60 dBFS, không clipping. Giọng Trúc Ly
VieNeu offline. SHA-256:
`2c76019c58ab2266662f1bca1dfcff2142da5112537cebe90825991a64b83d7f`.
Kiểm kỹ thuật/khung mẫu không thay xem/nghe toàn bộ; chưa đánh dấu QC cảm nhận.

Selected giữ nguồn `ddY5Hh29VhE`. Có 3 URL tìm trên web nhập metadata thủ công,
không phải search API tự động, không phải MP4 đã nhận hoặc được phép đăng lại.
Runner Flow lấy/chỉnh nguồn chưa nối, không dùng created để giả bản selected.

Các khoảng trống còn mở: catalog/ảnh/variant mới, owner confirmation cho tệp,
Flow capability/MP4 thật, OAuth YouTube, link/SKU mới, publisher hai nhánh/daily,
retention/click/commission có attribution. Không bật publisher cũ hoặc lịch mới.
Không có video mới công khai hay tiền mới phát sinh ở lượt này. Tổng 312 views
chỉ snapshot 03/10; hoa hồng hiện chưa biết.

Tài liệu nhúng đã đối chiếu: [YouTube player parameters](https://developers.google.com/youtube/player_parameters)
và [embed/privacy-enhanced player](https://support.google.com/youtube/answer/171780?hl=en).
Iframe dùng host youtube-nocookie và referrer policy có origin; CSP chỉ cho phép
host ảnh/player cần thiết, không mở script/connect ra mọi domain.
