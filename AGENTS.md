# Hướng dẫn phát triển

Đọc README và docs/architecture.md trước khi thay đổi ranh giới dịch vụ.
Các skill của dự án ở .agents/skills/; chọn đúng skill theo nhiệm vụ.

- API quản lý ở services/control-api/src/affiliate_control; giao diện ở apps/console.
- Logic sản phẩm/nội dung ở packages/domain/src/affiliate_domain; không nhập HTTP/Docker vào domain.
- n8n chỉ điều phối. Tệp nguồn ở orchestration/n8n; triển khai ở infra/docker.
- Mục tiêu mỗi tệp mã ≤200 dòng, giới hạn cứng 250; mỗi hàm ≤60 dòng.
  Đây là quy ước của dự án, không phải chuẩn quốc tế. Ngoại lệ phải được ghi trong ADR.
- Không đưa token, session trình duyệt, dữ liệu n8n, media hoặc log vào Git.
- Không sửa payload/mã băm job đã đăng. Tạo revision mới khi thay đổi bản dựng.
- Adapters có side effect phải dùng ID cho phép, timeout và khóa/idempotency.
- Dữ liệu thiếu là null. Thời điểm quan sát và hạn sử dụng đi cùng bằng chứng.
- Không đổi lịch/publisher live trong một lần refactor. Kiểm tra chuyển đổi rồi mới cutover.
- Xác thực thay đổi ảnh hưởng phiên, chạy luồng, link và đăng bài bằng các kiểm thử hành vi.

Mã legacy đang chạy ngoài repository; adapter chỉ gọi ba luồng đã khai báo.
Repository này chưa thay thế toàn bộ runtime. Đọc docs/phases.md để biết phần đã làm.
