# Tài khoản, session và API

Module đăng nhập xã hội mới chưa triển khai trong MVP. Console chỉ quan sát khả
năng đã có qua báo cáo và adapter. Không nhập lại mật khẩu hoặc session hiện tại.

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
[YouTube videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert),
[n8n API authentication](https://github.com/n8n-io/n8n-docs/blob/main/docs/connect/n8n-api/authentication.md),
[TikTok Direct Post](https://developers.tiktok.com/doc/content-posting-api-get-started/),
[Flow credits](https://support.google.com/flow/answer/16526234?hl=en).
Pro credits trên Flow được theo dõi riêng; không coi đó là tiền cấp cho Veo API.
