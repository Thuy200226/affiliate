---
name: affiliate-production
description: Tạo và vận hành hai video affiliate độc lập — tự dựng và từ nguồn được chọn — với kiểm tra chất lượng, link đúng SKU và account/topic.
---

Đọc docs/two-video-workflow.md và docs/operations.md. Mỗi batch đúng hai nhánh:
created tự dựng, selected dùng chính video chọn từ danh sách. Không gộp, không
đổi selected thành created hoặc chỉ chèn Flow intro. Source thay chỉ invalidate
selected; script thay chỉ invalidate created. Bài/hash cũ không đổi. Đọc
requirements-matrix/workflow-cases khi nghiệm thu; plan B-only trước là lịch sử.

“Nhạy cảm” đã làm rõ là gây chú ý/tranh luận, không phải tình dục. Giữ raw query,
tiêu chí/prompt Settings có version; đề cử có giải thích, selected tách recommended.
Search/ranking không lọc theo quyền. Chủ xác nhận sau selection; Settings dùng lại
xác nhận hợp lệ theo source/hash/phạm vi để bỏ hỏi lặp, không bypass unknown.

Tìm video theo topic/SKU và nguồn/time/metric có bằng chứng. Nguồn được phép dùng
mới vào media library; nguồn khác dùng nghiên cứu rồi viết storyboard mới.
Edit người là một bước có request/consent/rights và QC trước/sau; kiểm capability
Flow trên tài khoản thật, không giả face-edit đã chạy. Không dùng xoá watermark/
đổi mặt để hợp thức hóa video người khác. Thiếu điều kiện giữ đúng selection/bước,
không âm thầm thay source hoặc bỏ yêu cầu edit.

Chọn hook cụ thể, giọng rõ, nhịp nhanh, CTA ở cuối hợp lý. Không thêm lời về AI/
hình minh hoạ/thu nhập vào video; giữ metadata cần thiết của nền tảng. Sản phẩm,
variant, claim và link phải đối chiếu trước release.

Xem/nghe cả video, ghi lỗi theo timecode. Release bind revision/hash/account/link.
CTA theo vị trí link nhấp được; YouTube Shorts đi qua profile, không bảo người xem
copy URL. Hashtag bám đúng topic/sản phẩm. Kiểm account mapping khi đăng nhiều kênh.

Auto là mode mục tiêu mặc định cho route đủ điều kiện; owner hold/reject phải bền
vững và kiểm lại trước gửi. Warning phong cách không tự chặn auto; blocker quyền/
link/SKU/file/capability vẫn phải xử lý. Back xem dữ liệu; rerun tạo revision và
invalidate dependencies, worker cũ không ghi vào bản mới.

Reserve publish key trước upload; kết quả chưa rõ thì reconcile, không đăng lại mù.
Đánh giá retention/click/approved commission bằng dữ liệu riêng. Không hứa doanh thu
từ view. Review/auto là mode account đã chọn, không bắt review tay mọi job auto.
Review mỗi phase ít nhất hai lượt khác phương pháp, ghi lỗi và retest; kiểm thử
console không chứng minh Flow/full automation hoặc hoa hồng đã đạt.
