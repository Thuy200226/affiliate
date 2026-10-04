const ResultsView = (() => {
  let signature = "";
  function metric(value, unit = "") {
    if (!["number", "string"].includes(typeof value) || (typeof value === "string" && !value.trim())) return "Chưa có dữ liệu";
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 ? number.toLocaleString("vi-VN") + unit : "Chưa có dữ liệu";
  }
  function draw(data) {
    const ui = window.AffiliateUI, next = JSON.stringify([data.videos, data.observed_at, data.snapshot_fresh, data.metrics_error]);
    document.getElementById("sync-results").disabled = data.actions.find((a) => a.key === "readiness")?.enabled !== true || data.running === true;
    document.getElementById("results-status").textContent = data.metrics_error ||
      `Nguồn YouTube · quan sát ${ui.date(data.observed_at)}${data.snapshot_fresh ? "" : " · dữ liệu cũ, cần cập nhật"}.`;
    if (signature === next || document.querySelector("#videos iframe") || document.activeElement?.closest("#results-table")) return;
    signature = next;
    const cards = document.getElementById("videos"), rows = document.getElementById("results-rows");
    cards.replaceChildren(); rows.replaceChildren();
    const videos = data.videos.filter((v) => /^[A-Za-z0-9_-]{11}$/.test(v.video_id));
    for (const video of videos) {
      const publicVideo = video.privacy_status === "public", title = video.title || `Video ${video.video_id}`;
      const privacy = {public:"Công khai", private:"Riêng tư", unlisted:"Không công khai"}[video.privacy_status] || "Chưa xác minh";
      const card = ui.node("article", undefined, "published-card"); card.id = `post-${video.video_id}`;
      card.append(ui.node("p", privacy.toUpperCase(), publicVideo ? "pill" : "pill private"));
      card.append(MediaPreview.create(`https://www.youtube.com/watch?v=${video.video_id}`, title, publicVideo), ui.node("h3", title));
      card.append(ui.node("p", `${metric(video.total_platform_views)} lượt xem · ${ui.date(video.observed_at)}`, "muted"));
      card.append(ui.link(`https://www.youtube.com/watch?v=${video.video_id}`, "Mở bài trên YouTube"));
      const inspect = ui.node("button", "Xem kết quả bài này", "secondary");
      inspect.addEventListener("click", () => {
        document.getElementById("result-filter").value = video.video_id; filterRows(video.video_id);
        document.getElementById("results").scrollIntoView({behavior:"smooth"});
      }); card.append(inspect); cards.append(card);
      const row = ui.node("tr"); row.dataset.video = video.video_id;
      const name = ui.node("th"); name.scope = "row"; name.append(ui.link(`https://www.youtube.com/watch?v=${video.video_id}`, title), ui.node("small", video.video_id));
      row.append(name);
      for (const value of [privacy, metric(video.total_platform_views), metric(video.likes), metric(video.comments),
        "Chưa có dữ liệu", "Chưa có dữ liệu", "Chưa có dữ liệu", ui.date(video.observed_at)]) row.append(ui.node("td", value));
      rows.append(row);
    }
    if (!cards.children.length) {
      cards.append(ui.node("p", "Chưa có bài đăng được ghi nhận."));
      const empty = ui.node("tr"), cell = ui.node("td", "Chưa có bài đăng để đối chiếu kết quả.");
      cell.colSpan = 9; empty.append(cell); rows.append(empty);
    }
    const select = document.getElementById("result-filter"), prior = select.value;
    select.replaceChildren(ui.node("option", "Tất cả bài đăng")); select.options[0].value = "";
    for (const video of videos) {
      const option = ui.node("option", `${video.title || "Video"} · ${video.video_id}`); option.value = video.video_id; select.append(option);
    }
    select.value = [...select.options].some((o) => o.value === prior) ? prior : ""; filterRows(select.value);
  }
  function filterRows(id) {
    document.querySelectorAll("#results-rows tr").forEach((row) => {row.hidden = !!id && row.dataset.video !== id;});
  }
  if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", () => document.getElementById("result-filter").addEventListener("change", (e) => filterRows(e.target.value)));
  return {draw, metric};
})();
if (typeof module !== "undefined") module.exports = ResultsView;
