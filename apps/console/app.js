const el = (id) => document.getElementById(id);
let csrf = "";
let busy = false;
const pendingKeys = new Map();
const labels = { trends: "Trend", media: "Video", readiness: "Kiểm tra" };
const statuses = { running: "Đang chạy", succeeded: "Thành công", failed: "Thất bại", interrupted: "Bị ngắt · cần đối chiếu", uncertain: "Chưa rõ · cần đối chiếu" };
const blockers = {
  live_trend_to_product_and_matching_video_template_not_connected: "Trend → sản phẩm → kịch bản mới chưa nối.",
  verified_fashion_catalog_missing: "Catalog thời trang chưa được kiểm chứng.",
  Instagram_TikTok_Meta_publishing_connection_not_verified: "Quyền đăng TikTok/Meta chưa được kiểm chứng.",
  automatic_public_release_disabled: "Tự công khai video chưa được triển khai.",
  clickable_channel_funnel_not_verified: "Đường nhấp từ hồ sơ tới sản phẩm cần kiểm chứng mới.",
  product_UI_evidence_missing_or_expired: "Bằng chứng SKU/giá sản phẩm cần làm mới.",
};
function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
}
function notice(text, error = false) {
  el("notice").textContent = text;
  el("notice").classList.toggle("error", error);
}
async function request(path, options = {}) {
  const response = await fetch(path, { ...options, credentials: "same-origin" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Không đọc được kết quả.");
  return data;
}
function date(value) {
  return value ? new Date(value).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" }) : "Chưa có";
}
function link(url, text) {
  const item = node("a", text);
  const parsed = new URL(url);
  if (parsed.protocol !== "https:") return node("span", text);
  item.href = parsed.href;
  item.target = "_blank";
  item.rel = "noopener noreferrer";
  return item;
}
function drawActions(actions) {
  el("actions").replaceChildren();
  for (const action of actions) {
    const card = node("article");
    card.append(node("h3", action.title));
    const copy = action.reason || (action.key === "media" ? "Dựng/tải riêng tư job đã đủ điều kiện." : "Chạy workflow hiện có và ghi kết quả.");
    card.append(node("p", copy));
    const button = node("button", "Chạy luồng");
    button.disabled = !action.enabled || busy;
    button.addEventListener("click", () => run(action.key));
    card.append(button);
    el("actions").append(card);
  }
}
function drawOverview(data) {
  csrf = data.csrf_token;
  el("worker").textContent = data.worker_ok ? "Khả dụng" : "Chưa kết nối";
  const publicVideos = data.videos.filter((v) => v.privacy_status === "public");
  el("count").textContent = publicVideos.length;
  const counts = publicVideos.map((v) => v.total_platform_views);
  el("views").textContent = counts.length && counts.every((v) => v !== null && v !== undefined)
    ? counts.reduce((sum, v) => sum + Number(v), 0).toLocaleString("vi-VN") : "Chưa biết";
  el("commission").textContent = data.confirmed_commission === null ? "Chưa biết" : String(data.confirmed_commission);
  el("observed").textContent = `Bản ghi video: ${date(data.observed_at)}${data.snapshot_fresh ? "" : " · cần làm mới"}.`;
  drawActions(data.actions);
  el("blockers").replaceChildren(...data.blockers.map((b) => node("li", blockers[b] || b)));
  el("accounts").replaceChildren(...data.connections.map((c) => {
    const item = node("article"); item.append(node("h3", c.title), node("p", c.status)); return item;
  }));
  el("link-route").replaceChildren(node("span", "Link đã cấu hình: "));
  el("link-route").append(data.affiliate_url ? link(data.affiliate_url, "Mở sản phẩm trên Shopee") : node("span", "Chưa có"));
  el("videos").replaceChildren(...data.videos.filter((v) => /^[A-Za-z0-9_-]{11}$/.test(v.video_id)).map((v) =>
    link(`https://www.youtube.com/watch?v=${v.video_id}`, `${v.video_id} · ${v.privacy_status === "public" ? "Công khai" : "Riêng tư"} · ${v.total_platform_views ?? "?"} lượt xem`)));
}
function drawRuns(data) {
  busy = data.runs.some((r) => r.status === "running");
  el("runs").replaceChildren(...data.runs.map((r) => {
    const row = node("tr");
    const detail = r.result.message || (r.result.ok ? "Đã nhận kết quả từ workflow" : r.status === "failed" ? "Workflow báo lỗi · kiểm tra kết nối/log cục bộ" : "—");
    for (const text of [labels[r.flow] || r.flow, date(r.started_at), statuses[r.status] || r.status, detail]) row.append(node("td", text));
    return row;
  }));
  if (!data.runs.length) { const row = node("tr"); const cell = node("td", "Chưa có lượt chạy từ trang quản lý này."); cell.colSpan = 4; row.append(cell); el("runs").append(row); }
}
async function refresh(showNotice = false) {
  try {
    const [overview, history] = await Promise.all([request("/api/overview"), request("/api/runs")]);
    drawRuns(history); drawOverview(overview);
    if (showNotice) notice(busy ? "Một luồng đang chạy. Kết quả sẽ cập nhật tại lịch sử." : "Đã đọc trạng thái. Bạn có thể chạy từng luồng khả dụng bên dưới.");
  } catch (error) { notice(error.message, true); }
}
async function run(flow) {
  const key = pendingKeys.get(flow) || crypto.randomUUID();
  pendingKeys.set(flow, key);
  busy = true;
  document.querySelectorAll("#actions button").forEach((button) => { button.disabled = true; });
  try {
    const result = await request(`/api/actions/${flow}`, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify({ idempotency_key: key }) });
    pendingKeys.delete(flow);
    notice(`Đã nhận lượt ${labels[flow]}: ${result.run.id.slice(0, 8)}. Xem tiến độ tại lịch sử.`);
  } catch (error) { notice(error.message, true); }
  await refresh();
}
el("refresh").addEventListener("click", () => refresh(true));
refresh(true);
setInterval(() => refresh(), 10000);
