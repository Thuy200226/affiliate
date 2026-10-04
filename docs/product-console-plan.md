# Kế hoạch tối ưu trang quản lý sản phẩm và nội dung

**Bản lịch sử A/B — đã được thay thế bởi [kế hoạch B-only hiện hành](b-only-console-plan.md).**
Chỉ tham khảo các quyết định cũ; không dùng tài liệu này để tạo A cho job mới.

Ngày: 04/10/2026. Trạng thái: đặc tả triển khai, chưa phải tính năng đã chạy.
Phạm vi: mở rộng console hiện có, không xây lại một hệ thống song song.
Ngân sách tiền mới: 0; triển khai trên máy hiện tại, ưu tiên YouTube trước.

## 1. Kết quả cần đạt

Chủ tài khoản mở một trang và trả lời được: đang quảng bá sản phẩm nào, bài nào
đang tăng tương tác, bản nào chuẩn bị đăng, vì sao đang chờ và có thể đăng ngay không.
Mọi bài có thể truy ngược tới sản phẩm, biến thể, video, tài khoản và link của chủ.
Lịch tự động và nút đăng tay dùng cùng một hàng đợi và sổ xuất bản.

Hai nghĩa của “sản phẩm đang lên” phải tách riêng:

- **Đang quảng bá:** đã có bài công khai được đối chiếu trên tài khoản của chủ.
- **Có tín hiệu tăng:** lượt xem/tương tác nội dung tăng theo cửa sổ đo; hoặc tín hiệu
  thị trường có nguồn. Không coi tăng lượt xem là tăng đơn hàng của sản phẩm.

## 2. Khoảng cách của bản hiện tại

Console chỉ có tổng quan, bản ghi video, kết nối và ba nút trends/media/readiness.
`overview.py` lấy link hợp lệ đầu tiên trong hàng đợi; chưa đủ cho nhiều sản phẩm.
Chưa có catalog, bảng số liệu theo sản phẩm, bản xem trước hàng chờ hoặc đăng công khai.
Lượt kiểm tra 04/10 lỗi xác thực YouTube; bản ghi lượt xem gần nhất là 03/10.
Shopee chưa có báo cáo mới đủ để gán click/hoa hồng cho từng video.

Giữ adapter đang chạy; không bật publisher cũ để lấp chỗ thiếu. Không chuyển số
liệu cũ thành “trực tiếp”. Đọc [đánh giá code](code-review.md) trước khi chuyển module.

## 3. Bố trí màn hình

Thanh bên: Tổng quan · Sản phẩm · Đang quảng bá · Khám phá · Chờ đăng · Lịch đăng ·
Tài khoản · Nhật ký. Mỗi trang giữ bộ lọc và URL chi tiết để mở lại đúng đối tượng.

| Màn hình | Nội dung chính | Thao tác |
|---|---|---|
| Tổng quan | số sản phẩm/bài công khai, bản sẵn sàng, việc bị chặn; dữ liệu cập nhật lúc nào | đi tới đúng hàng chờ/lỗi, làm mới số liệu |
| Sản phẩm | ảnh, shop/item/biến thể, chủ đề, link theo kênh, giá/tồn kho nếu có bằng chứng mới | thêm ứng viên, đối chiếu sản phẩm, tạo batch A/B |
| Đang quảng bá | sản phẩm → bài → nền tảng/tài khoản; số liệu 24h/7 ngày và link bài thật | mở bài, xem hiệu quả, tạo bản mới, tạm dừng bài tương lai |
| Khám phá | tín hiệu thị trường/nguồn video có ngày, khu vực, mức liên quan và quyền sử dụng | đưa vào nghiên cứu, ghép đúng SKU, tạo brief |
| Chờ đăng | bản A/B, preview, tiến độ, điểm chưa đạt, giờ/kênh dự kiến | xem/sửa, duyệt, đăng ngay, hẹn giờ, giữ lại |
| Lịch đăng | lịch theo ngày/kênh/chủ đề, sức chứa và trạng thái thực tế | đổi giờ chưa đăng, chuyển review/auto, tạm dừng/tiếp tục |
| Tài khoản | danh tính, quyền đọc/đăng/gắn link, phiên/quota | kết nối lại bằng chủ tài khoản, kiểm tra quyền |
| Nhật ký | từng bước, đầu vào/revision, lỗi, thời điểm, kết quả và permalink | mở lỗi, đối chiếu bài, chạy lại bước an toàn |

Mobile hiển thị thẻ sản phẩm; desktop hiển thị bảng. Tên nút tiếng Việt, không yêu
cầu người dùng biết workflow ID. Có tìm kiếm, phân trang, lọc tài khoản/chủ đề/A-B.
Empty state phân biệt “chưa có bản” với “không đọc được dữ liệu”.

## 4. Sản phẩm và trang Đang quảng bá

Một hàng là một sản phẩm/biến thể, mở ra danh sách bài; không lấy tiêu đề làm khóa.
Khóa sản phẩm: sàn + shop_id + item_id; biến thể có ID riêng. Một link không đại diện
cho toàn bộ catalog. Không tự gán tất cả video hiện có cho M31 chỉ từ tên file.

Các cột: ảnh/tên/biến thể, chủ đề, số bài công khai, tổng lượt xem có phạm vi rõ,
lượt xem mới 24h, like/comment/share nếu đọc được, giữ người xem, click/đơn/hoa hồng,
tuổi dữ liệu, tài khoản và trạng thái link. Metric thiếu hiển thị “chưa có dữ liệu”.

Trang chi tiết có bốn tab: Sản phẩm · Bài đã đăng · Nội dung chuẩn bị · Hiệu quả.
Mỗi bài hiển thị video A/B, giờ công khai, đúng tài khoản, mô tả/hashtag/link placement,
URL bài, lịch sử số liệu và lỗi đồng bộ. Riêng tư không nằm trong tổng bài công khai.
Các bài nhiều sản phẩm ở nhóm riêng; không cộng toàn bộ lượt xem cho từng SKU.

“Tạm dừng sản phẩm” chỉ ngừng job/lịch tương lai cho SKU đó; không xoá/ẩn bài cũ.
“Tạo bản tiếp theo” tạo revision/job mới, không sửa mã băm của video đã xuất bản.

## 5. Khám phá và đánh giá tín hiệu tăng

Khám phá có hai tab: thị trường bên ngoài và hiệu quả trên kênh của chủ. Nguồn
phải có URL, thời gian, khu vực, topic/SKU match và metric quan sát được. RSS trend
chỉ là tín hiệu quan tâm tìm kiếm, không chứng minh doanh số Shopee hoặc video viral.

Chỉ tính tốc độ tăng khi có các mốc đo so sánh được. Giữ riêng từng nền tảng và
tuổi bài; không xếp một video cũ nhiều view trên video mới chỉ vì tổng lớn hơn.
Lọc đúng topic/SKU, nguồn còn mới và khả năng dựng trước; sau đó xếp theo tốc độ
tăng, giữ người xem và chất lượng dữ liệu. Có giải thích cạnh mỗi gợi ý.

Nhãn ban đầu: Có tăng quan sát được · Tăng nhanh hơn kỳ trước · Mẫu nhỏ · Chưa đủ
hai kỳ · Dữ liệu cũ. Ngưỡng mẫu/cửa sổ là cấu hình có phiên bản; hiệu chỉnh sau khi
có dữ liệu kênh, không gắn nhãn “sẽ bán chạy”. Xem [hợp đồng số liệu](metrics-contract.md).

Nguồn video chỉ dùng dựng lại khi có quyền; nếu không, nghiên cứu hook/nhịp để
làm storyboard mới. Không bổ sung bước xoá nguồn/watermark hay đổi mặt để đăng lại.

## 6. Chờ đăng và review từng bước

Mỗi thẻ gồm sản phẩm, biến thể, A/B, tài khoản đích, lịch dự kiến, revision,
thumbnail/MP4, thời lượng và trạng thái. Chia nhóm: Đang làm · Cần xử lý · Chờ duyệt ·
Sẵn sàng · Đang đăng. Bản đã đăng chuyển sang registry, không còn nút đăng lại.

Khi mở bản: phát toàn bộ video, nghe giọng, đọc lời/phụ đề/mô tả/hashtag; xem từng
scene và lỗi tại timecode. B là nhiều cảnh Flow liền mạch xuyên suốt, không phải intro.
Mỗi bước có “Xem kết quả”, “Chạy bước này” hoặc lý do chưa thể chạy.

Cho sửa brief, lời, mô tả và hashtag ở bản nháp. Sửa media/copy/SKU/link/account tạo
revision mới, bỏ duyệt cũ và chạy lại các kiểm tra phụ thuộc. Duyệt gắn đúng video hash.
Không đưa nội dung hướng dẫn công cụ/thu nhập chủ kênh vào giọng hoặc hình video;
giữ thông tin thương mại/thiết lập nền tảng cần thiết ở vị trí thích hợp.

## 7. Đăng tay bằng một click có kiểm soát

Đường chính: Chờ đăng → mở preview → Duyệt → Đăng ngay → xác nhận đích → xem tiến độ.
Không yêu cầu sao chép URL affiliate. Cửa sổ xác nhận hiện tên/avatar tài khoản,
nền tảng, sản phẩm/biến thể, A/B, video, copy, hashtag và nơi link xuất hiện.

Trước khi bật nút, kiểm tra: revision đã duyệt, media/QC đạt, danh tính/quyền đăng,
bằng chứng sản phẩm/link còn hạn, chủ link đúng, cấu hình nền tảng và giới hạn đăng.
Hiển thị checklist và lý do thiếu; không chỉ trả một lỗi “không hợp lệ”.

Server lấy nội dung bất biến theo ID/revision, không nhận path hay lệnh từ trình
duyệt. Giữ chỗ đích đăng bằng transaction; click lặp trả cùng run. Lịch chạy đồng
thời bị giữ bởi cùng publish key, kể cả nút UI và n8n có idempotency key khác nhau.

Tiến trình: Giữ chỗ → tải/xử lý → đối chiếu metadata/quyền xem → công khai nếu đủ
điều kiện → xác minh permalink/placement. Chỉ báo “đã đăng công khai” sau readback.
Nếu đã có staging riêng tư đúng revision, release bản đó thay vì tải lại.
Kết nối không cho phép public thì giữ riêng tư và nêu rõ, không báo thành công giả.

Timeout sau khi gửi phải vào “Đang đối chiếu”; không tự tải lại. Nếu thất bại rõ
trước gửi có thể retry an toàn. Hủy chỉ áp dụng trước khi bắt đầu upload/release;
đã gửi thì chờ đối chiếu, không hứa thu hồi bài. Không có thao tác xóa bài hàng loạt.

Khi nền tảng chưa có connector: “Chuẩn bị gói đăng tay” xuất MP4 + copy + hashtag +
hướng dẫn đặt link; mở trang đăng của đúng nền tảng. Chủ tự upload, nhập permalink.
Registry giữ “Chủ đã khai báo, chưa xác minh” đến khi có readback đúng account/media.
Đây là phương án tay, không được ghi là đăng tự động. Không xuất session/token.

## 8. Link affiliate, topic và tài khoản

Link record gắn chủ affiliate + sản phẩm/biến thể + chiến dịch + nền tảng/tài khoản
+ vị trí. Connector sinh link bằng tài khoản của chủ; không dùng link đầu tiên cho
mọi SKU và không tự sửa query của link đã ký. Chứng cứ redirect không chứng minh
thuộc đúng chủ; phải có bằng chứng từ phiên/báo cáo affiliate.

YouTube Shorts: dùng link hồ sơ có tên đúng sản phẩm hoặc Shopping nếu đủ điều kiện,
không coi URL mô tả/comment là link nhấp được. Long-form có cấu hình mô tả riêng.
Theo [YouTube Help](https://support.google.com/youtube/answer/13748639?hl=en), vị trí
link có giới hạn; không hứa có thể đặt link nhấp ở mọi chỗ hoặc tự sửa profile qua API.

Nhiều sản phẩm: giữ tên/link hồ sơ ổn định, kiểm tra dung lượng/vị trí còn đủ; không
ghi đè M31 bằng sản phẩm mới khiến CTA bài cũ sai. Nếu cần trang tổng hợp, thiết kế
riêng sau khi có chỗ hosting khả dụng, không tự mua tên miền/dịch vụ.
Click dùng chung hồ sơ không tự chia cho video A/B; sub-ID chỉ dùng nếu nguồn hỗ trợ.

Routing table: topic → SKU đủ điều kiện → format → account → placement → lịch/mode.
Chủ nhìn thấy, chỉnh và tạm dừng từng hàng. Hashtag ngắn, đúng sản phẩm/topic,
không thêm tag không liên quan. Meta/TikTok chỉ mở nút đăng khi kiểm tra được quyền.

## 9. Bố trí dữ liệu và mã

SQLite dùng cho single-host; migration có phiên bản và backup/restore test trước cutover.
Media/báo cáo thô/session ở private runtime, DB chỉ giữ ID/ref/hash, không đưa vào Git.

| Thành phần | Dữ liệu/trách nhiệm |
|---|---|
| catalog | Products, Variants, ProductEvidence, Topics; TTL giá/claims/stock |
| discovery | TrendSignals, SourceVideos, RightsEvidence; nguồn và match SKU |
| content | Batches, Jobs, Revisions, Artifacts, StepRuns, Reviews; A/B độc lập |
| distribution | AccountRoutes, AffiliateLinks, Schedules, Publications; đích đăng |
| analytics | MetricObservations, SyncRuns, AttributionGroups; nguồn/coverage/kỳ đo |
| connections | identity, capability, credential/profile reference; không trả secret |

Domain chia catalog/content/distribution/metrics; API chia routes/read-models/use-cases;
console chia views/components/api-client. Không nối thêm mọi thứ vào `app.js` hoặc
`overview.py`. Source file mục tiêu ≤200 dòng, cứng 250; hàm ≤60 theo AGENTS.md.
n8n chỉ gọi ID job/bước và API điều phối; không render, lưu token hay tính tài chính.
Docker service quản lý/API độc lập worker media/connector; không mount Docker socket
hoặc profile trình duyệt vào UI. Chưa cần Redis hay tách quá nhiều microservice.

API planned: xem danh mục/chi tiết sản phẩm, bài/số liệu, discoveries, hàng chờ/review,
chạy bước, yêu cầu publish, trạng thái publish, lịch và connections. Xem [API](api.md).
GET có phân trang/filters; POST có phiên/CSRF/idempotency/revision. Không sửa qua GET.

## 10. Thứ tự triển khai và nghiệm thu

Đây là các lát cắt C1–C6 của [phase kiến trúc](phases.md), không tạo lịch/publisher thứ hai.

| Lát cắt | Việc giao được | Phụ thuộc | Nghiệm thu |
|---|---|---|---|
| C1 · dữ liệu và đọc | catalog/registry/migrations, ghép bài cũ bằng bằng chứng, bảng Đang quảng bá, nguồn/tuổi số liệu | phase 2, khôi phục YouTube OAuth cho số liệu mới | 3 bài public tách 2 bản private; SKU đúng; dữ liệu thiếu/cũ không thành 0 |
| C2 · hàng chờ và review | A/B queue, preview ID an toàn, checklist, sửa/duyệt, timeline bước | C1 + phase 4 | xem toàn bộ MP4; sửa làm mất duyệt cũ; bản intro không qua QC của B |
| C3 · đăng tay YouTube | connector/capability, link theo SKU, publish ledger chung, modal, progress/readback | C2 + phase 3/5 | 1 bản được chọn đăng đúng account; click/cron/restart không tạo bản trùng; có URL thật |
| C4 · hiệu quả/khám phá | observations, biểu đồ, delta/ranking có nguồn, Shopee report mapping nếu đọc được | C1 + quyền Analytics/báo cáo | metric/coverage chính xác; CTR không gán sai; sửa số liệu không tạo tăng giả |
| C5 · lịch daily | scheduler một chủ sở hữu, review/auto per route, caps/pause/quota/reconcile | C2/C3 + B đủ cảnh + nguồn/link hợp lệ | quan sát ≥7 ngày; có bản mới đủ điều kiện, không trùng; UI/n8n cùng trạng thái |
| C6 · thêm nền tảng | spike quyền đọc/đăng/link từng tài khoản; connector hoặc gói đăng tay | C3/C5 + khả năng thực tế | từng nền tảng có bài/URL/placement được xác minh trước khi bật lịch |

C1 có thể giao giao diện với dữ liệu lịch sử khi OAuth chưa khôi phục, nhưng phải
ghi tuổi dữ liệu. Không coi đó là nghiệm thu số liệu mới. C2 có thể chạy độc lập
bằng media hợp lệ; C3 public phải chờ đúng quyền và approval. Chưa chốt thời hạn
cho phần quyền API/Flow khi chưa hoàn tất kiểm tra khả năng và hạn mức.

## 11. Kiểm thử bắt buộc và vận hành

Fixture sạch: 2 SKU, nhiều account, A/B riêng, 1 video nhiều SKU, dữ liệu null/stale,
kỳ báo cáo lệch múi giờ, OAuth hết hạn, link sai chủ/variant, upload timeout.
Test transaction/concurrency cron+UI, double-click, sửa revision sau duyệt, restart
ở giữa upload, link hồ sơ bị thay đổi, platform private-only và nhập permalink sai.
Test preview không nhận path tùy ý; API/log/export không chứa token/profile/session.

Giao từng lát cắt bằng adapter → test → shadow read → đối chiếu → cutover một route.
Không chạy shadow upload. Docker mới không ảnh hưởng dự án khác hoặc volume cũ.
Thử restore catalog/ledger rồi mới chuyển lịch, giữ rollback không làm bài bị đăng lại.

Mốc giao diện refresh DB khi có sự kiện, hoặc poll nhẹ; không biến mỗi lần mở màn
hình thành một lượt gọi API ngoài. Ban đầu gom số liệu mỗi 3 giờ khi quota cho phép,
Analytics/báo cáo affiliate theo kỳ nguồn khả dụng; lịch đăng daily là cấu hình riêng.
Một sản phẩm/YouTube trước; mở rộng sau C3, không mất thời gian nối tất cả mạng cùng lúc.

Mức hoàn tất: chủ dùng được danh mục → review → đăng tay → mở URL → xem dữ liệu theo
đúng SKU/account; sau đó chứng minh lịch daily chạy/recover/pause. Video được tải lên
không tự chứng minh nội dung cuốn hút hoặc có hoa hồng; đánh giá bằng dữ liệu thật.
