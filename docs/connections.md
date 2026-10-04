# Tài khoản, session và API

Console đã có Settings cho chín công cụ: YouTube, YouTube search, Shopee, Flow,
Gemini, TikTok, Instagram, Facebook, n8n. Module connections lưu key/token bằng
macOS Keychain (helper native nhận qua stdin), SQLite chỉ lưu tool/saved_at.
Không trả lại giá trị bí mật, không ghi vào args/log/response/Git.
Nút mở Chrome dùng URL chính thức cố định, hồ sơ 0700 ở .local/browser-profiles.
Hồ sơ mới không tự sao chép phiên Chrome chủ đang dùng. Login được giữ bởi Chrome;
không xuất cookie/session. api_verified luôn false cho tới khi có probe identity/scope.
YouTube search đã dùng key đã lưu; các key khác chưa chứng minh executor hoạt động.
Linux/Docker chưa có Keychain/profile Mac; UI không giả thao tác này thành công.

| Dịch vụ | Cách nối đích | Có thể tự động khi | Khi cần chủ tài khoản |
|---|---|---|---|
| n8n | credential references + authenticated webhook | workflow deployed và service token đúng | cấu hình credential ban đầu |
| YouTube | OAuth2, channel identity, videos/analytics | scope/refresh/quota hợp lệ | consent hoặc token hết hạn |
| Shopee Affiliate | connector được account cấp hoặc UI được phép | link/report capability đã xác nhận | login/xác minh, quyền affiliate |
| Google Flow | owner local browser profile | session/quota/tác vụ UI hợp lệ | CAPTCHA, terms, quyền ảnh, login lại |
| TikTok | Content Posting API | account scope + app audit phù hợp | OAuth/app onboarding |
| Meta | publishing connector đúng Page/pro account | identity/scope/permission đã kiểm tra | OAuth/approval ban đầu |

OAuth tokens nằm trong n8n encrypted store hoặc OS keychain; DB chỉ giữ credential_ref.
Web profiles nằm ngoài repo, quyền 0700, không share giữa accounts, không export cookie.
Session service giữ account_id, auth_kind, state, expires_at, last_checked_at,
needed_action, reference. UI chỉ hiển thị metadata đã redacted.

OAuth login có state một lần, PKCE khi provider hỗ trợ, callback allowlist và kiểm
account identity sau consent. Session transitions: unknown → ready → expired hoặc
needs_owner → ready. Không dùng kết quả HTTP 200 ở trang login để đánh dấu ready.

Kết nối API không đồng nghĩa quyền publish. Capability check riêng: read_metrics,
generate_affiliate_link, upload_private, publish_public, attach_product, place_link.
Đăng nhập web không tự cấp những quyền này.

Nguồn chính thức đã kiểm tra:
[YouTube videos.delete](https://developers.google.com/youtube/v3/docs/videos/delete),
[TikTok embed player](https://developers.tiktok.com/docs/en/embed-player),
[YouTube videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert),
[n8n API authentication](https://github.com/n8n-io/n8n-docs/blob/main/docs/connect/n8n-api/authentication.md),
[TikTok Direct Post](https://developers.tiktok.com/doc/content-posting-api-get-started/),
[Flow credits](https://support.google.com/flow/answer/16526234?hl=en).
Pro credits trên Flow được theo dõi riêng; không coi đó là tiền cấp cho Veo API.
