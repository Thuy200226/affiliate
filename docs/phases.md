# Kế hoạch triển khai theo phase

Ngày lập: 04/10/2026. Ngân sách tiền mới: 0. Ưu tiên một topic/SKU và YouTube đã
có kết nối trước, rồi mới mở rộng. Hai video là hai sản phẩm độc lập trong cùng batch.

## Phase 0 — Đánh giá và chuẩn bị Git

Đã thực hiện: review đường đi hiện tại; tách repo sạch; chuẩn module/file/hàm;
gitignore; docs/skills; checker trước Git. Không copy secret hoặc video.

Nghiệm thu: mã kiểm tra đạt, nguồn rõ ràng, không có dữ liệu cá nhân/session được
staged, xác định repository đích. Push cần URL repository và quyền tài khoản tương ứng.

## Phase 1 — Console vận hành

Bản đầu trong repo: đọc trạng thái thật, nút chạy trends/readiness/media đủ điều kiện,
lịch sử bền vững, khóa chạy, idempotency, phiên same-origin. Không fake bước chưa nối.

Tiếp theo: preview media theo ID có kiểm soát; timeline từng scene; nhật ký từng
bước và pause riêng các lịch của dự án sau khi chuyển scheduler về một chủ sở hữu.
Nghiệm thu: click và nhận run_id; restart không mất lịch sử; click lặp không chạy
trùng; dữ liệu thiếu hiện “chưa biết”; lỗi được báo đúng bước.

## Phase 2 — Domain, queue và n8n

Chuyển load_jobs/state/reserve khỏi worker 400 dòng; dùng SQLite cho bản single-host,
Postgres chỉ khi chạy đa worker hoặc trên server. Chưa cần Redis/microservice quá nhiều.
Generator n8n chỉ chứa HTTP steps/IDs; secrets do credential store quản lý.

Catalog phải có variant/connector/claim evidence/rights. Trend discovery được cấu
hình nguồn/topic, không gắn một trend bất kỳ vào SKU. “Viral” dựa vào view velocity,
engagement và thời điểm có nguồn; không lấy tổng views khác tuổi để xếp hạng đơn giản.

Nghiệm thu: reserve cùng batch từ cron/UI chỉ có 1 batch; A và B hai job độc lập;
không đổi fingerprint của job cũ; TTL hết hạn thì refresh hoặc giữ lại đúng bước.

## Phase 3 — Tài khoản, session và nguồn video

API account dùng OAuth/credential reference hiện có; mỗi account có identity, scopes,
expires_at, topics, quota, link placement, daily cap. Phiên web Flow ở local profile
riêng, login tương tác lần đầu, khóa một profile một worker. UI cho xem trạng thái,
mở login và tiếp tục job; không có nút tải cookies/token.

Danh mục video tìm được lưu URL, creator, topic, SKU, thời điểm, metrics nguồn và
quyền sử dụng. Nếu được phép tải/dựng lại thì lưu media hash + license reference.
Video khác chỉ dùng nghiên cứu hook/nhịp/cách kể, rồi tạo storyboard mới.
Không lấy việc xoá watermark/đổi mặt làm bằng chứng có quyền đăng lại.

Browser Flow runner chỉ triển khai khi thao tác được nền tảng cho phép và hạn mức
thực tế đủ. Có needs_owner cho login/CAPTCHA/quyền ảnh. Không gọi endpoint web
nội bộ hoặc trích xuất cookie để giả một API Veo miễn phí.

Nghiệm thu: account identity đúng; session restart an toàn; không lộ credential;
nguồn mỗi asset có hồ sơ; credit ledger và timeout; trạng thái blocked không loop vô hạn.

## Phase 4 — Tạo hai video hoàn chỉnh

A: brief → hook 1–2 giây → voice cục bộ → motion graphics → subtitles → CTA.
B: nghiên cứu video phù hợp → storyboard mới → ≥3 Flow shots nhất quán toàn bộ
khung hình → ghép liên tục → voice/subtitles tùy brief → CTA. Không chỉ thêm Flow intro.
Tái dùng cảnh có quyền trong thư viện và dựng bản mới theo topic để tiết kiệm tín dụng.

Chỉ nhận định product đúng model/variant, không dùng cảnh không khớp làm demo thật.
Copy ngắn tích cực; không nói production tools/thu nhập của chủ kênh trên video.
Hook có thể tương phản, hài hước hoặc gây tranh luận về lựa chọn sản phẩm bằng
thông tin kiểm chứng. Không tạo tình dục tường minh, bịa công dụng hay giả trải nghiệm.

Nghiệm thu: hai MP4 độc lập; toàn bộ decode/voice/captions; nghe và xem toàn bộ,
SKU nhất quán, không che watermark; bản chưa đạt không release. Kiểm tra kỹ thuật
không tự suy thành video thu hút. Review rubric ghi rõ lỗi cần sửa theo timecode.

## Phase 5 — Link và xuất bản từng account

Ưu tiên YouTube hiện có. Facebook Page/Reels tiếp theo nếu đúng account và đủ quyền.
Instagram/TikTok chỉ đưa vào lịch sau khi capability và link placement được kiểm tra.
Không coi việc login trên web hoặc liên kết Shopee là cấp quyền API đăng video.

AffiliateLink: owner_account + shop_id + item_id + variant + platform + campaign
+ topic + destination evidence. Không tự thêm query làm hỏng chữ ký hoặc tracking.
Link mới phải được sinh trong chính tài khoản affiliate qua connector được phép.
Hash/copy/account/link binding đi cùng revision. Short description không có URL nhấp
được thì CTA dẫn đúng vị trí nền tảng hỗ trợ. Hashtag bám sản phẩm/topic/nội dung,
không thêm hashtag không liên quan chỉ vì đang nổi.

Nghiệm thu: private staging → processing verified → metadata/link check → release
đúng mode của account → permalink registry. Cùng publish key chỉ có một bài.
[YouTube Shorts](https://support.google.com/youtube/answer/13748639?hl=en) không cho
nhấp URL mô tả/comment; dùng profile hoặc Shopping nếu account đủ điều kiện.
[TikTok Direct Post](https://developers.tiktok.com/doc/content-posting-api-get-started/)
giới hạn client chưa audit ở private; phải xử lý điều kiện này trước lịch public.

## Phase 6 — Lịch hằng ngày và đánh giá

Scheduler theo Asia/Ho_Chi_Minh: thu thập nguồn → tạo batch → chạy A/B → release theo
account/topic → đo sau các mốc thời gian. Giờ cụ thể được chọn sau dữ liệu kênh;
không tuyên bố một giờ đăng tốt nhất khi chưa có dữ liệu. Ban đầu daily cap 1 bài/
account cho một loại nội dung; A/B có thể phân ngày để không đăng hai bản gần trùng.

Queue có concurrency cap, retry safe reads, backoff, dead-letter và spending limit.
Tín dụng Flow là quota riêng; hết quota thì giữ B chờ, không mua thêm hoặc bật API phí.
Theo dõi dữ liệu đủ tuổi: exposure, stayed/swiped, completion, average percentage,
organic clicks, đơn chờ, commission approved, paid amount. Tự-click tách riêng.

Nghiệm thu: chạy liên tục ít nhất 7 ngày quan sát thực tế hoặc một chu kỳ quota;
mỗi ngày có batch/topic/account đúng, không trùng, link đúng, có registry/report,
restart/reconcile/pause hoạt động. Chỉ nói có doanh thu khi commission được xác nhận.

## Phase 7 — Cutover và bàn giao

Chuyển lịch từng phần từ legacy; backup có restore test, khóa versions/digests,
CI secret scan/test/line limit; tag release; runbook account/session recovery.
Sau khi đủ bằng chứng mới ngừng lịch cũ. Chưa xoá runtime/volume hoặc media hiện có.

Thứ tự tối ưu thực tế: 0–1 → 2 → 3/4 → 5 YouTube → 6 → mở rộng nền tảng → 7.
Không cam kết “tối ưu nhất thế giới”; chọn cải tiến từ lỗi quan sát và metric thật.
