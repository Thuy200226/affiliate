# Hợp đồng dữ liệu hiệu quả sản phẩm

Ngày: 04/10/2026. Thiết kế planned cho trang Đang quảng bá/Khám phá; chưa triển khai.
Phải đọc cùng [kế hoạch console](product-console-plan.md). Không gọi mọi metric là
“tương tác sản phẩm”: phân biệt hiệu quả nội dung, tín hiệu thị trường và affiliate.

## 1. Đơn vị quan sát

Mỗi observation giữ: provider, account_id, external_object_id, publication_id nếu
đối chiếu được, metric_name, value/unit, counter_kind (cumulative/period/rate),
period_start/end, provider_timezone, observed_at, source_ref, definition_version,
status, attribution_scope và denominator nếu là tỷ lệ. Giá trị thiếu là null.

Status: available, stale, insufficient_data, unsupported, permission_denied,
sync_failed. Lượt đọc lỗi ghi SyncRun; không thay observation tốt cũ bằng 0.
Giữ cả dữ liệu thô/reference và bản chuẩn hóa ở private runtime; không lưu trong Git.
Unique source key/upsert để lần import lại không cộng thêm số liệu. Lưu lịch sử chỉnh
sửa của provider, không giả định bộ đếm luôn tăng. Không lưu thông tin cá nhân người mua.

Provider xác định kỳ đo/múi giờ; UI đổi giờ hiển thị sang Asia/Ho_Chi_Minh nhưng không
tự gán lại số liệu theo “hôm nay” Việt Nam nếu nguồn báo cáo theo kỳ khác.

## 2. Metric theo nguồn

| Nhóm | Trường hiển thị | Nguồn/cách lấy | Giới hạn |
|---|---|---|---|
| Bài công khai | views, likes, comments, privacy, URL | Data API/connector cho đúng external ID | snapshot, không phải người xem duy nhất |
| Analytics của chủ | engaged views, share, watch time, average duration/percentage, retention nếu hỗ trợ | OAuth Analytics và tổ hợp report hợp lệ | có độ trễ; đọc API thử trước khi bật từng trường |
| Studio bổ sung | ở lại/bỏ qua, completion hoặc metric chưa có API đúng nghĩa | phiên chủ/export được phép, có timestamp | không suy từ views/engaged views; không giả tự động |
| Affiliate | click, đơn chờ, đơn hợp lệ, hoa hồng ước tính/duyệt, đã trả | báo cáo chủ affiliate/connector được phép | gán theo campaign/sub-ID nếu báo cáo có; không suy từ view |
| Thị trường | lượt tìm kiếm, view nguồn, sold/review nếu nguồn hiển thị | nguồn công khai/phiên được phép, có URL/kỳ | counter listing không chứng minh doanh số trong kỳ |

Khả năng YouTube: [Data API videos.list](https://developers.google.com/youtube/v3/docs/videos/list)
có statistics/status; [Analytics reports](https://developers.google.com/youtube/analytics/channel_reports)
cần quyền của chủ kênh, lọc theo video/kỳ. Metrics như engagedViews, likes/comments,
shares, averageViewDuration/Percentage và retention có [định nghĩa riêng](https://developers.google.com/youtube/analytics/metrics).
Không coi mọi metric xuất hiện trong Studio đều sẵn qua cùng endpoint. Báo cáo thử
kiểm tra quyền và tổ hợp filter trước; field không hỗ trợ vẫn hiện trạng thái rõ ràng.

Shopee/Meta/TikTok: chưa xác minh trong dự án có API cho toàn bộ các trường trên.
Làm capability spike bằng tài khoản hiện có; báo cáo nhập tay dùng schema cùng
loại, hiện nguồn “chủ nhập” và không nâng thành “API đã xác minh”. Không tạo scraper
vượt CAPTCHA hoặc trích xuất phiên để giả connector.

## 3. Tính tăng trưởng và tương tác

Views mới quan sát = C(t2) − C(t1), chỉ khi cùng bài/metric/definition, t2 > t1.
Views/giờ = chênh lệch / số giờ thực tế; cửa sổ 3/6/24h chỉ tính nếu có mốc hợp lệ.
Thiếu mốc đầu hoặc nguồn đã cũ trả null; không giả kỳ trước bằng 0. Counter giảm
được ghi “provider điều chỉnh”; không dùng chênh lệch âm làm tín hiệu giảm nhu cầu.
Không nội suy để vẽ một đường mượt rồi gọi đó là lượt xem thật.

Tăng tốc chỉ khi có hai cửa sổ liền nhau, tương đương độ dài/nguồn, đủ coverage và
mẫu. Kỳ trước = 0 thì không hiển thị vô hạn phần trăm. Nêu chênh lệch tuyệt đối.
Nếu chỉ có một kỳ, nhãn “có lượt xem mới” chứ không “đang tăng nhanh hơn”.

Engagement/view (%) = 100 × (likes + comments + shares trong kỳ) / views trong kỳ,
nếu cả ba thành phần có dữ liệu cùng định nghĩa/kỳ. Nếu share thiếu, hiển thị riêng
like/comment, không gọi tỷ lệ một phần là tỷ lệ đầy đủ. Không trộn counter lifetime
với view 24h hoặc chia interaction delta không tương thích cho period metric.

Các chỉ số retention giữ đúng tên/định nghĩa nguồn; tỷ lệ xem trung bình không phải
tỷ lệ xem hết và không tự cắt về 100%. Đường retention dùng mốc thời gian tương ứng
đúng revision video; không tính “thắng A/B” chỉ từ tổng lượt xem hai bài khác tuổi.

Xếp hạng trên kênh: cùng platform/format và cửa sổ tuổi bài → đủ mốc mới → tốc độ
views, retention khả dụng → dấu hiệu tương tác. Hiện công thức/nguồn và nhãn mẫu nhỏ.
Giai đoạn đầu gợi ý để chủ chọn; không tự public vì một điểm xếp hạng cao.

## 4. Tổng hợp về sản phẩm

PublicationProducts chứa primary SKU và các SKU phụ nếu có. Bài đơn sản phẩm được
gom theo SKU/variant; bài đa sản phẩm có bucket “nhiều sản phẩm”, không nhân views
cho mọi SKU. Overview toàn kênh dedupe theo provider/account/external_id.

Khi thiếu số liệu ở một bài: hiển thị “tổng đã biết” + coverage X/Y, không gọi đó
là tổng đầy đủ. Chỉ so/rank các hàng đủ coverage tương đương. Cross-platform có thể
hiện tổng lượt phát đã biết, nhưng không gọi tổng đó là unique viewers hoặc cộng
các tỷ lệ. Tỷ lệ tổng hợp cần denominator phù hợp; không lấy trung bình % các bài.

## 5. Click, attribution và doanh thu

LinkCampaign giữ owner affiliate, SKU, account/platform, placement, campaign/sub-ID
và source evidence. Không tự thêm sub-ID vào link ngắn đã ký. Connector phải sinh
link và xác nhận báo cáo dùng được trường attribution đó.

Phân cấp attribution: video → campaign → SKU → tài khoản → chưa gán. Gán ở mức
nguồn chứng minh được; nhiều video chung link hồ sơ chỉ hiện campaign/account,
không chia đều click/đơn cho video. Link có đúng SKU không chứng minh click từ bài.

Click tự kiểm thử ghi riêng theo sự kiện có bằng chứng. Nếu nguồn không cho tách,
hiển thị “click tổng, chưa tách kiểm thử”, không trừ số ước lượng hoặc gọi organic.
CTR sản phẩm chỉ tính nếu click và denominator đo cùng phạm vi/kỳ được định nghĩa.
Clicks Shopee / toàn bộ Shorts views không phải CTR đo được của từng video.

Đơn chờ, hoa hồng ước tính, hoa hồng đã duyệt và số tiền đã trả là trường riêng;
đơn trùng/status thay đổi phải đối chiếu theo ID nguồn. Số tiền đã trả toàn tài khoản
không tự chia cho SKU. YouTube ad revenue không thay thế doanh thu Shopee affiliate.
0 chỉ hợp lệ khi nguồn báo 0 cho đúng kỳ đầy đủ; không có nguồn là “chưa biết”.

## 6. Đồng bộ, lỗi và cấu hình

UI chỉ đọc DB; nút “Làm mới” tạo một sync job có khóa/debounce, không spam API.
Khởi điểm: counters mỗi 3h trong quota; Analytics/affiliate theo kỳ báo cáo khả dụng.
TTL counters khởi điểm 6h; đã quá hạn vẫn hiện số cũ + timestamp, không dùng xếp hạng
mới. Metric kỳ báo cáo dùng covered_through/next_expected_at, không TTL 6h máy móc.
Các giá trị này là cấu hình vận hành ban đầu, không phải cam kết độ tươi của provider.

Lỗi quyền pause đúng connector, các module khác tiếp tục. Lỗi quota chờ tới mốc cho
phép; network retry backoff có giới hạn. UI ghi lỗi lần đọc mới nhất cạnh số cũ.
Nhật ký không chứa token; refresh OAuth/phiên do chủ thực hiện khi cần.

## 7. Nghiệm thu dữ liệu

- Import lại cùng báo cáo không tăng counter/hoa hồng; giữ period/timezone đúng.
- Snapshot cũ/null/lỗi xác thực không hiển thị 0 hoặc “hôm nay”.
- Kỳ trước = 0, counter chỉnh giảm và share thiếu không sinh xếp hạng/CTR giả.
- Hai bài cùng link không được cấp click video-level nếu nguồn chỉ có campaign.
- Video private/technical test và multi-SKU không làm tăng tổng public/SKU sai.
- Đối chiếu một kỳ YouTube/Shopee với nguồn chủ tài khoản; sai số/độ trễ được ghi rõ.
