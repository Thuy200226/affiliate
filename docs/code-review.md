# Đánh giá trước khi chuyển Git — 04/10/2026

Phạm vi: runtime affiliate-automation trên máy chủ tài khoản và báo cáo hiện có.
Đây là review mã/kiến trúc, chưa phải audit toàn bộ secrets hoặc mọi dependency.

## Kết quả

Hệ thống legacy chạy n8n và worker, đã tải video, nhưng chưa hoàn thành luồng
tạo nội dung mới rồi đăng hằng ngày. Báo cáo ngày 03/10 vẫn ghi fully_automated=false.
Ba video công khai có bản ghi tổng lượt xem 69, 240, 3; đây là số liệu ở thời điểm
quan sát, không phải số liệu trực tiếp ngày 04/10. Hoa hồng xác nhận hiện chưa biết.

| Ưu tiên | Bằng chứng trong code | Tác động | Cách xử lý |
|---|---|---|---|
| P0 | .gitignore chỉ 5 dòng; private/artifacts/dist/transfer nằm cùng code | dễ đưa tài khoản, session, backup/media vào Git | repo sạch allowlist, scan staged files, không copy runtime |
| P1 | local_video_worker.py 400 dòng; load_jobs gắn cứng 1 SKU/link/2 kiểu trình bày | không mở rộng topic/account/định dạng B | tách queue, job contract, voice, renderer, inspector, uploader adapters |
| P1 | run_existing_affiliate_flow.py chạy CLI, không có khóa chung với schedule | nút UI, heartbeat và lịch có thể chạy trùng | API reserve idempotent + scheduler chung; khóa cross-process trước cutover |
| P1 | header worker local-v1 là hằng số; loopback là ranh giới hiện tại | không đủ cho nhiều người dùng hoặc expose mạng | giữ loopback, thêm phiên/CSRF cho console; service token khi triển khai mới |
| P1 | B dùng flow_clean intro-only; full_flow_story.py chưa được worker gọi | B chưa đúng yêu cầu video xuyên suốt | nhánh full_flow có ≥3 cảnh, timeline/voice/QC, immutable revision |
| P1 | giá/quyền ảnh/funnel/metrics lấy snapshot tệp | thiếu dữ liệu mới làm batch khó tự chạy | bằng chứng có TTL, connector refresh, needs_owner/blocked reason cụ thể |
| P1 | reserve() khóa upload trước gọi API; không retry khi kết quả chưa rõ | giảm đăng trùng nhưng job có thể treo | reconciliation bằng upload ID/hash, không retry mù |
| P2 | README/ARCHITECTURE ghi bản 15/09 và Spark, lịch mới ở upgrade | người mới hiểu sai hệ thống | một kiến trúc chuẩn, bảng legacy→module và trạng thái phase |
| P2 | macOS Swift renderer và path Homebrew/venv gắn cứng | Docker Linux không tự chạy renderer | worker host riêng; FFmpeg portable ở phase sau, không đổi âm thầm |
| P2 | kiểm tra từ khóa thiếu candidates; chưa nối candidate tới catalog | lịch trend thành công chưa sinh video | nhiều nguồn có timestamp; chấm relevance→match SKU→brief |

## Phần tốt cần giữ

Job/media đã đăng được cố định bằng mã băm; upload reserve/ack có cơ chế chống
lặp; JSON/XML giới hạn kích thước; Flow manifest kiểm tra nguồn và nhiều cảnh;
kiểm tra giải mã, định dạng và âm thanh; n8n bind loopback; thiếu metric giữ null.
Không đổi các invariants này khi tái tổ chức thư mục.

## Mức rủi ro chuyển đổi

Không di chuyển trực tiếp upgrade/ hoặc volume đang chạy. Dùng adapter trước,
chuyển từng module với các fixture sạch và kiểm thử hợp đồng. Private state của
runtime không trở thành fixture. Bản đăng cũ giữ nguyên fingerprint.

Không có git remote trong các thư mục đã kiểm tra. Chưa push ra dịch vụ ngoài.
Không kết luận repo không có secret chỉ bằng một regex; scanner mới là cổng ban đầu.

## Lượt kiểm tra thật từ console

04/10: nút kiểm tra đã gọi đúng workflow 3c40800415102804 và ghi lịch sử thất bại.
Lỗi NodeApiError tại bước đọc YouTube; chẩn đoán cục bộ có tín hiệu lỗi authorization/
token expired hoặc revoked. Chưa xác định chính xác expired hay revoked; cần refresh
kết nối qua chủ tài khoản. Không gọi upload/public release hoặc coi số liệu cũ là mới.
Đây là lỗi connector legacy, không phải kết quả kiểm thử đơn vị của console.
