# Review mở rộng danh mục và console — 04/10/2026

Phạm vi: nhiều sản phẩm/nhóm hàng, ưu tiên/bỏ qua, nguồn đa nền tảng, preview
nguồn/đầu ra, kết quả từng bài, xoá bài, Settings và thống kê affiliate.
Không chuyển lịch/publisher live, sửa bài đã đăng hoặc phát sinh tiền mới.

## Vòng 1 — code, dữ liệu và kiểm thử tự động

- Catalog kiểm Shop/Item/variant/account/platform/placement; link Shopee giữ nguyên,
  ảnh chỉ CDN Shopee. Không nhận trường provenance giả từ browser.
- Snapshot batch bất biến. Skip giữ hai nhánh; restore không tự bỏ hold. Đổi source/
  upload chỉ invalidate selected khớp ID, không sửa created.
- Keychain helper biên dịch thật; secrets qua stdin, không args/DB/public response.
  Chrome profile riêng 0700, URL cố định, không xuất cookies. Tests key/launch dùng
  mock; chưa lưu key hoặc chứng minh login mới qua nút này.
- MP4 giới hạn 100 MB/180 giây, full decode/hash, containment và Range. Output cần
  xác nhận đúng hash nguồn; không tự gọi file nhận là đã chạy Flow/đổi mặt.
- Xoá YouTube chỉ ID registry, typed ID/permanent, ownership probe, reserve trước
  DELETE. Timeout/crash giữ uncertain, không gửi xoá lần hai hoặc Bearer qua redirect.
  Kiểm API bằng mock, không xoá video thật.
- Báo cáo cùng phạm vi/kỳ thay thế, không cộng trùng. Tổng đơn/ước tính không suy
  ra đơn/hoa hồng duyệt/paid hoặc attribution từng video.
- 65 ca test đạt sau mở rộng; 12 module JavaScript kiểm cú pháp đạt; gate 96 file
  nguồn và 56 file staged kiểm dòng/hàm/secret/artifact đạt. Diff whitespace đạt.
  Kiểm kỹ thuật không chứng minh hiệu quả kinh doanh. Ba skill đã rà frontmatter/
  nội dung thủ công; quick_validate chưa chạy được vì môi trường thiếu PyYAML.

Lỗi tìm và sửa: provider source cũ; thiếu empty-state/bỏ ưu tiên; bảng/card khác
cách render metric; preview cứng Shorts cho mọi route; placeholder created bảo
chọn nguồn; file nhận bị gọi “đã dựng”; reuse confirmation chưa so hash.

## Vòng 2 — trình duyệt, fixture cách ly và tệp thực

Console thật: per-post button lọc đúng uMAWQBq5u7k, 240 views tại snapshot 03/10
17:00:49 VN; metric thiếu giữ unknown. Không refresh giả số liệu OAuth lỗi.
Mobile 390×844: main/section/card không tràn viewport, bảng dài cuộn trong khung.
Reset viewport về mặc định sau test.

scripts/qa_console.py dùng ba fixture thời trang/nhà cửa/công nghệ và nguồn
example.org, không phải sản phẩm/link bán thật. Bridge không gọi live flow;
key/profile actions bị chặn. Test UI:

1. Home chỉ hiện hộp đựng; beauty hiện empty-state rõ.
2. Sửa tiêu đề rồi đổi sản phẩm: huỷ giữ draft đúng, tiếp tục đổi đúng source/batch.
   Dùng hộp hỏi trong trang, không browser confirm gây kẹt.
3. Upload MP4 tự dựng: full decode đạt, browser readyState 4, 15s, 1080×1920,
   error null.
4. Xác nhận fixture đúng hash, nhận output: player trước/sau đều 15s/1080×1920,
   readyState 4, error null. Cùng file để test transport, không thử đổi mặt.
5. Không duyệt perceptual hoặc public publish từ kết quả kiểm kỹ thuật.

Bước chọn tệp qua công cụ browser chậm bất thường (một lượt >20 phút), chưa xác
định nguyên nhân. Kết quả cuối đúng nhưng không nghiệm thu tốc độ/unattended browser
automation. HTTP tests/native decode độc lập đạt; cần đo chooser/network/inspection
riêng khi nối browser runner. Không lặp upload để che lỗi.

Generic native renderer: fixture 15s/360 khung, H264 1080×1920, AAC48k stereo;
SHA 980be906cbb3e17a6f01d8477c1e90145fcadcdff52b8be901aa0aa5bc93970e.
Full decode đạt, peak -1.3913 dBFS/RMS -18.1891 dBFS, clipped ratio 0. Đã nhìn
khung đầu; mẫu trung tính chưa có ảnh SKU mới hoặc bằng chứng giữ người xem.
Perceptual_reviewed vẫn false.

## Tài khoản thật và phần còn thiếu

Chrome Shopee chủ đang login. Dashboard kỳ 03/10/2026 có click 0, đơn 0, hoa hồng
ước tính 0 ₫. Đã ghi console đúng account scope; duyệt/paid chưa biết. Banner yêu
cầu thiết lập thanh toán để nhận hoa hồng, không tự điền thông tin tài chính.
Danh sách sản phẩm bị CAPTCHA, giữ trang chờ chủ. Catalog thật vẫn một M31;
không tạo sản phẩm hoặc affiliate link giả để lấp UI.

Chưa nghiệm thu: auto fetch/link/report Shopee; tải mọi nguồn tự động; Flow/edit
người; OAuth/readback mới; publisher hai nhánh/đa nền tảng; daily scheduler.
Settings key/profile không thay cho scope/identity/executor. Chưa có bằng chứng
hoa hồng xác nhận/tiền đã trả; không tuyên bố doanh thu.

## Thứ tự tiếp tục

1. Chủ giải CAPTCHA; lấy feed/link thật và báo cáo có kỳ/nguồn.
2. Probe account/scope, import catalog/report chính thức theo idempotency.
3. Nhận source được dùng, kiểm Flow/edit thực, chạy trước/sau và QC.
4. Nối publisher hai nhánh, staging/readback/link đúng SKU/account, rồi cutover
   một lịch daily. Không bật publisher cũ hoặc đăng các revision gần trùng.
