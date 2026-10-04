# Kiểm thử workflow hai video và hai lượt review

Ngày 04/10/2026. Đây là **ma trận cần triển khai**, không phải kết quả tests đã đạt.
Kết quả thật được ghi riêng trong validation/audit report, theo phạm vi đã chạy.
Tham chiếu: [plan](two-video-workflow.md), [requirements](requirements-matrix.md).

## Lượt 1 — review contracts và unit/domain tests

Rà state transitions, revision/input hash, nguồn/quyền/consent, account/link,
raw query/profile version, transaction/idempotency và không lưu secrets trong Git.
Kiểm module/tệp/hàm, dependency, migrations/backup và side effects.

## Lượt 2 — review hành vi, UI và dịch vụ

Chạy API/UI với dữ liệu chuẩn lẫn thiếu/lỗi, concurrent commands, restart giữa bước,
quota/session, upload uncertain và sync partial. Nghe/xem **toàn bộ B thực tế** khi
có MP4; không dùng placeholder hoặc fixture graphics để chứng nhận video Flow.
Đối chiếu remote account/SKU/link/permalink bằng phương thức được phép, không tạo
views/click giả hoặc mua hàng test. Review runtime khác unit tests của console.

| ID | Case | Kết quả bắt buộc |
|---|---|---|
| W01 | batch có một video tự tạo và một video chọn nguồn | đúng created+selected, không gộp hoặc giả source bằng created; bài cũ bất biến |
| W02 | RSS trend chạy thành công nhưng không có video | discovery trống đúng nghĩa, không sinh URL/điểm giả |
| W03 | kết quả không có SKU rõ | vẫn xem nghiên cứu; không tự gán link sản phẩm |
| W04 | query gây tranh luận hợp lệ | raw query giữ nguyên, lý do provider từ chối hiển thị nếu có |
| W05 | metadata không đủ chấm hook/độ hấp dẫn | unknown, không gắn “nhạy nhất/viral chắc chắn” |
| W06 | nguồn trùng URL/hash từ nhiều query | dedupe, giữ nhiều provenance/query refs |
| W07 | media/audio/face permission thiếu hoặc hết hạn | giữ selection, blocker đúng bước; không đổi nguồn âm thầm |
| W08 | đổi nguồn trước xử lý | revision mới, invalidation đúng DAG |
| W09 | đổi nguồn khi worker đang chạy | fencing ngăn ghi vào revision mới; lịch sử kết quả cũ giữ |
| W10 | sửa query Settings giữa batch | batch cũ giữ snapshot; apply requires revision |
| W11 | bấm Back rồi Next không sửa | không rerender, không tăng quota; kiểm dependencies |
| W12 | bấm Làm lại từ đây | preview impact, revision/run mới, không ghi đè artifact đã đăng |
| W13 | hai tab sửa cùng revision | 409/conflict, không lost update |
| W14 | reload/restart sau source selection/hold | lựa chọn và hold còn, không tự public |
| W15 | worker chết/mất heartbeat | interrupted/lease recovery; không retry có side effect mù |
| W16 | Flow cần login/CAPTCHA/terms | needs_owner; Settings tới đúng bước, không bypass/lặp thông báo |
| W17 | hết quota/cash=0 | chờ quota, không mua thêm hoặc bật API phí |
| W18 | Flow model/account không hỗ trợ edit source | capability false/unknown, giữ job; không giả face-swap |
| W19 | có người nhưng tuổi/danh tính chưa biết | không suy quyền/consent từ ảnh; kiểm hồ sơ trước edit |
| W20 | request đổi mặt nhưng output chưa đổi/không ổn định | QC fail có timecode; không báo hoàn tất hoặc bỏ request |
| W21 | Flow generation timeout sau tiêu credit | reconcile generation ID; không generate lại mù |
| W22 | scene sai SKU/biến thể, loop/freeze padding | QC fail; không public |
| W23 | media hỏng, audio clipping, giọng kém, caption lệch | giữ chờ sửa, lỗi timecode; technical pass ≠ quality pass |
| W24 | sửa lời/CTA hoặc account/link sau duyệt | invalidation/binding mới; không dùng approval cũ |
| W25 | warning phong cách gây tranh luận, đủ điều kiện auto | text warning ở UI, không tự hold hoặc chèn vào giọng |
| W26 | hard blocker bị gửi override từ trình duyệt | server giữ blocker, không bypass bằng UI |
| W27 | chủ Giữ lại trước reservation/gửi | publisher không gửi; hold không mất do lịch/refresh |
| W28 | chủ Giữ lại sau upload bắt đầu | trạng thái đúng thời điểm, reconcile; không hứa thu hồi kịp |
| W29 | UI+cron+heartbeat cùng publish | một reservation/upload, tất cả trỏ cùng run |
| W30 | timeout/restart sau upload, chưa nhận video ID | uncertain; đối chiếu trước gửi thêm |
| W31 | staging riêng tư cũ khác revision/hash | không public staging sai; giữ private |
| W32 | credential đúng Google nhưng sai channel | chặn trước post, hiện identity mismatch |
| W33 | app/provider chỉ cho private hoặc scope thiếu | giữ private/blocked, không báo public |
| W34 | link đúng sàn nhưng sai chủ/shop/item/variant | fail binding, không release |
| W35 | đổi profile link làm CTA bài cũ sai | chặn route mới, không ghi đè đường cũ |
| W36 | Shorts đặt URL mô tả rồi coi clickable | fail placement; dùng profile/Shopping đủ quyền |
| W37 | gói đăng tay đã tải MP4 nhưng chưa có URL | chưa đăng; permalink khai báo cần readback |
| W38 | nút sync bấm liên tục/network retry | một sync theo phạm vi/kỳ, không tạo upload |
| W39 | OAuth đọc metric lỗi | giữ snapshot+timestamp, stale/permission_error, không 0 |
| W40 | vài bài có metric, vài bài thiếu | tổng đã biết + coverage, không tổng đầy đủ giả |
| W41 | counter giảm hoặc kỳ trước=0 | điều chỉnh provider, không growth% vô hạn/xếp hạng giả |
| W42 | hai nhánh chung link/campaign | không cấp click per-video hoặc chia đều hoa hồng |
| W43 | affiliate order/commission đổi trạng thái/import lại | dedupe theo nguồn, approved/paid riêng, không cộng trùng |
| W44 | video private/technical test/đa-SKU | không tăng tổng public/SKU sai |
| W45 | key/API/body/path/source URL bất thường | schema/CSRF/host/allowlist, không arbitrary command/SSRF/path traversal |
| W46 | key/profile/log/credential export đi vào source/API | secret/artifact gate fail, không lộ qua UI |
| W47 | máy ngủ/Docker/worker không có | báo unavailable; không tuyên bố lịch đã chạy |
| W48 | hai lịch cũ/mới cùng daily batch | unique batch + deployment ledger, không double publisher |
| W49 | restore DB nhưng bài remote đã có | reconcile registry/ledger trước mở publisher |
| W50 | đổi topic/SKU/account routing sai | chặn cross-account/cross-product, giữ lịch sử |
| W51 | quyền nguồn unknown khi tìm/đề cử | nguồn vẫn có trong danh sách/ranking; chờ chủ ở bước sau selection |
| W52 | chế độ dùng lại xác nhận, nguồn/hash/phạm vi khác | không áp xác nhận sai; chủ thấy đúng bước cần xác nhận |
| W53 | xác nhận hợp lệ cho cùng source/hash/phạm vi | không hỏi lặp; tiếp tục revision đủ điều kiện |

## Bằng chứng nghiệm thu

Mỗi case: input fixture sạch, action, expected/actual, run/test ID, timestamp,
revision/hash/source capability, verdict và issue khi fail. Không lưu cookie/token/
thông tin người mua vào report Git. Failed → fix → retest bắt buộc trước phase gate.

Cổng release: regression + transaction/race/API + UI smoke/keyboard/mobile + toàn bộ
MP4 QC + account/link/permalink readback + backup restore + ít nhất hai lượt review.
Hosted CI/Docker/Linux/mobile/social capabilities chỉ đánh dấu pass khi đã thử thật.

## Theo dõi kinh doanh không giả kết quả

Sau post: visibility/processing, nguồn traffic, stayed/retention khả dụng, click với
phạm vi attribution, đơn chờ/hoa hồng duyệt/tiền đã trả. Chưa có dữ liệu hoặc mẫu
nhỏ không kết luận thắng/thua. Thiếu engagement/commission phải tạo issue đúng funnel
và cải thiện revision tiếp theo, không báo thành công kinh doanh từ upload success.
