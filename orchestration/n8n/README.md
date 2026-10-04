# Ranh giới n8n

n8n gọi service qua HTTP có xác thực, truyền ID job/revision và nhận trạng thái.
Không nhúng code render, mật khẩu hay điều khiển trình duyệt vào Code node.

Ba workflow live được cầu nối legacy gọi hiện tại:

| Key | ID live | Tác dụng |
|---|---|---|
| trends | 9e14f52bf2202829 | đọc trend công khai |
| media | 04868d9653749779 | render/tải riêng tư job đủ điều kiện |
| readiness | 3c40800415102804 | đối chiếu video và phần còn thiếu |

ID là cấu hình triển khai, không phải token. Adapter hiện có không import,
activate hoặc sửa các workflow này. Chúng vẫn là workflow legacy ngoài repository.

Luồng đích: Schedule → reserve daily batch → discover → match product → chọn nguồn
→ chủ xác nhận nguồn hoặc dùng lại xác nhận hợp lệ → resolve owned affiliate link
→ B xuyên suốt → QC → review hoặc auto-release → publisher
→ verify processing/link → metrics. Mỗi bước trả run_id, status và artifact references.
Không lọc/rank quyền trong discovery; unknown chờ chủ sau selection, không thay
nguồn ngầm. Giữ release hold/revision và khóa chung với UI/heartbeat trước cutover.

Khi chuyển đổi: export bản không có credentials/execution data, thay credential ID
bằng reference triển khai, kiểm thử inactive, rồi cutover từng lịch. Không nhập các
publisher legacy hàng loạt. JSON export là build artifact; nguồn chuẩn là module
generator và contract version đã review ở phase 2.

Đã kiểm tra [Webhook chính thức](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/):
test URL và production URL khác nhau; production endpoint cần authentication.
Không coi đường /rest nội bộ của UI là API công khai ổn định.
