# Đối chiếu yêu cầu của chủ — hiện hành 04/10/2026

Các câu nói mới nhất thay thế yêu cầu mâu thuẫn trước đó, không cộng cả hai hướng.
Đặc tả chính: [workflow hai video](two-video-workflow.md). “Giữ” ở bảng này nghĩa
là có trong thiết kế; không đồng nghĩa tính năng đã code hoặc đã chạy thành công.

| ID | Yêu cầu đã đọc | Quyết định trong thiết kế | Nơi nghiệm thu |
|---|---|---|---|
| R01 | Dùng hệ thống sẵn, không xây một hệ thống khác | giữ repo/console/adapter, chuyển từng phần | P0/P5, architecture |
| R02 | Câu cũ bỏ A, tối ưu B | đã bị lời làm rõ R03 mới thay thế; giữ lịch sử | two-video-workflow |
| R03 | Một video tự làm, một video chọn từ danh sách tìm kiếm | đúng created+selected độc lập; không gộp, không chỉ B | P1–P3, test_two_video |
| R04 | Video nguồn xử lý xuyên suốt, không chỉ thêm Flow intro | selected dùng chính nguồn chọn; không padding hoặc đổi thành created | P3 |
| R05 | Tổng quan/thống kê hệ thống | các số lượng, lỗi và trạng thái thật | §2/P1 |
| R06 | Tổng hợp văn bản, hình sản phẩm, link | catalog/variant/evidence/brief, edit được | §3/P1/P2 |
| R07 | Link affiliate đúng của chủ, đúng SKU | owner/SKU/campaign/account binding | §8/P4 |
| R08 | Danh sách video sản phẩm tìm được | URL/creator/query/time/metrics/rights; không giả RSS thành video | §3/P2 |
| R09 | Ưu tiên video nhạy cảm/cuốn hút | đã làm rõ không phải tình dục; gây chú ý/tranh luận, đúng SKU | §1/3/P2 |
| R10 | Đề cử video gây chú ý nhất | ranking có chứng cứ/giải thích; unknown nếu chưa xem được | §3/P2 |
| R11 | Chủ đổi video dự kiến xử lý | recommended tách selected, revision và invalidation | §3/6/P2 |
| R12 | Đưa nguồn vào Flow | có nhánh edit nguồn được phép; kiểm capability/quota account thật | §4/P3 |
| R13 | Đổi mặt người nếu có | có edit_request, quyền nguồn/người, nhân vật được phép, trước/sau QC | §4/P3 |
| R14 | Từng yêu cầu cũ xoá nguồn để đăng lại | không triển khai che xuất xứ/video không có quyền; chữ của chủ chỉnh được | §4, blocker rõ |
| R15 | Nội dung tình dục theo câu cũ | chủ đã làm rõ không yêu cầu; không tiếp tục hiểu “nhạy cảm” là tình dục | §1 |
| R16 | Theo dõi tiến độ video/copy | bước/heartbeat/output thật; không timer % giả | §2/5/P2/P3 |
| R17 | Hai video hoàn chỉnh chờ đăng, dễ so sánh | created ↔ selected và nguồn/revisions; copy/link/QC riêng | P1–P3 |
| R18 | Mặc định đăng, chủ có thể không đăng | auto mục tiêu sau nghiệm thu; hold per job bền vững | §5/8/P4/P5 |
| R19 | Nhạy cảm chỉ cảnh báo text vẫn đăng | warning phong cách không chặn; technical/rights/platform blocker vẫn chặn | §5, W25/W26 |
| R20 | Hiển thị đã đăng, bài/link/tài khoản | registry/readback/visibility/hash; không gán private là public | §2/8/P4 |
| R21 | Kết quả đầy đủ, nút cập nhật mới nhất | sync run theo nguồn/kỳ, coverage, null/stale/error | §2/8, metrics-contract |
| R22 | Settings đăng nhập lại các tài khoản | provider-specific OAuth/profile, identity/capabilities, resume job | §7/P2/P3/P4 |
| R23 | Keys/UI phần liên quan chỉnh lại được | masked replace/revoke cho provider hỗ trợ; không lấy cookie thành API key | §7, connections |
| R24 | Sửa query/nội dung tìm kiếm trong Settings | raw query/prompt/profile version và impact preview | §3/7/P2 |
| R25 | Hướng dẫn trực quan, nhìn biết dùng | bảy khu vực, stepper, hành động/lý do/next_action, tour/helper | §2/7/P1 |
| R26 | Trở về bước trước và làm lại | view back ≠ rerun; DAG revision/lease/fencing | §6, W08–W15 |
| R27 | Đi tiếp bằng click | server transition/dependency/capability, không chỉ UI badge | §6/P2 |
| R28 | Tự tìm, xử lý và đăng daily theo topic/account | scheduler chung, caps/quota/batch unique và recover | §8/P5 |
| R29 | Tiếp tục kiểm tra mỗi 3h | cadence kiểm tra riêng; cutover đồng bộ heartbeat hai nhánh | P5 |
| R30 | Đa nền tảng khả thi, đúng link/hashtag | chỉ mở route đủ quyền; không coi login Shopee là quyền post mọi mạng | §8/P4/P5 |
| R31 | Không nói AI/tự động/mục đích/thu nhập trong video | giọng/chữ chỉ sản phẩm; metadata/provenance cần thiết vẫn giữ | §4/P3/P4 |
| R32 | Ngắn tích cực và hấp dẫn | hook/nhịp/visual/auditory QC; không bịa công dụng hoặc thử nghiệm | §4/10/P3 |
| R33 | Không đổi thông tin chưa chắc thành lời yếu | bỏ claim chưa có bằng chứng, không biến nó thành khẳng định giả | §3/4/P3 |
| R34 | Không phát sinh tiền mới, có Google Pro | cash=0, Flow quota ledger, không API phí/mua credit/ads | §1/4/8 |
| R35 | Code/module/folder chuẩn, skills, Git cá nhân | ranh giới module/line checks/CI/skills/personal repo | §9/P0, AGENTS |
| R36 | Review hoạt động và chuẩn dự án ít nhất hai lần | hai phương pháp/checklists, lưu lỗi và retest | §10, audit report |
| R37 | Tương tác/hoa hồng là mục tiêu | đo organic/retention/funnel/approved commission, không suy từ views | §10, metrics-contract |
| R38 | Hoàn hảo, không bỏ case/không bao giờ lỗi | thay lời bảo đảm bất khả thi bằng test matrix/observability/recovery có chứng cứ | §10, workflow-cases |
| R39 | Bỏ mọi “rule” cản tìm nội dung | raw query không bị âm thầm đổi; không bỏ xác minh nguồn/link/identity/permission | §3/5/7 |
| R40 | Chủ tự xác nhận nguồn sau khi tìm/chọn | search/ranking không lọc theo quyền; xác nhận owner riêng, giữ nguồn đã chọn | §3/P2/P3 |
| R41 | Setting bỏ xác nhận | hỗ trợ dùng lại xác nhận còn hiệu lực, không hỏi lặp; không bỏ quyền nguồn chưa xác nhận | §3/7, W51/W52 |

## Trạng thái triển khai tại lượt lập kế hoạch

Console bảy khu vực/ba action, workspace hai nhánh, source picker, edit kịch bản/
copy/hashtag/hold/revision, Settings và created renderer đã nối. Preview có Range.
Source URL đã có danh sách thực tế, search API adapter cần cấu hình key. Selected
confirmation/edit request lưu được nhưng Flow runner chưa nối; face-edit/publisher/
daily chưa có. Link/SKU cần refresh và OAuth legacy đang lỗi. Không đánh dấu mọi
hàng R05–R30 hoàn thành từ UI/tests. Xem review hai video để biết bằng chứng thật.
Phát hiện/tiêu chí có điều kiện vẫn hiện ở UI/backlog; không tự chọn phương án khác.

## Cổng bàn giao

Mỗi R giữ owner module, phase, test IDs, evidence/run ID và status delivered/planned/
needs_owner/blocked/not_supported/superseded. Khi thay đổi yêu cầu cập nhật phiên bản,
phạm vi invalidation, Settings và skills; không sửa lịch sử bài đăng. Owner phải nhìn
thấy yêu cầu có điều kiện/chưa hỗ trợ, không biến chúng thành hàng “hoàn tất”.
