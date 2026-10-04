const OutputView = (() => {
  const ui = () => Workspace.ui();
  const labels = {created: "1 · Video tự làm", selected: "2 · Video từ danh sách tìm kiếm"};
  const states = {draft: "Chưa xử lý", processing: "Đang xử lý", ready: "Đã dựng · chờ đánh giá", failed: "Chưa đạt", interrupted: "Bị ngắt · cần làm lại"};
  function draw(state, batch) {
    const processing = document.getElementById("processing-list"), outputs = document.getElementById("outputs");
    processing.replaceChildren(); outputs.replaceChildren();
    if (!batch) {outputs.append(ui().node("p", "Tạo batch để quản lý đúng hai video riêng biệt.")); return;}
    for (const kind of ["created", "selected"]) {
      const branch = batch.branches[kind], card = ui().node("article", undefined, "output-card");
      card.append(ui().node("h3", labels[kind]), ui().node("p", `Revision ${branch.revision} · ${states[branch.status]}${branch.hold ? " · ĐANG GIỮ" : ""}`, "pill"));
      if (branch.status === "processing") processing.append(ui().node("p", `${labels[kind]}: ${branch.notes.join(" · ")}`));
      if (branch.artifact) {
        const video = ui().node("video"); video.controls = true; video.preload = "metadata";
        video.src = `/api/content/media/${batch.id}/${kind}/${branch.revision}`;
        card.append(video, ui().node("p", `${branch.artifact.duration_seconds.toFixed(2)} giây · ${branch.artifact.width}×${branch.artifact.height} · kiểm kỹ thuật đạt`, "muted"));
        const download = ui().node("a", "Tải MP4 để đăng tay", "source-link"); download.href = video.src;
        download.download = `m31-${kind}-r${branch.revision}.mp4`; card.append(download);
        card.append(manualPackage(batch, branch));
        card.append(Workspace.button(branch.artifact.perceptual_reviewed ? "Đã đánh giá chất lượng" : "Đã xem/nghe và duyệt chất lượng", "review", {sha256: branch.artifact.sha256, watched_listened: true}, kind, branch.artifact.perceptual_reviewed));
        card.append(publicationPreview(batch, branch));
      } else card.append(ui().node("div", branch.notes.join(" · ") || "Chưa có tệp hoàn chỉnh. Chọn nguồn và xử lý để xem bản cuối tại đây.", "pending-preview"));
      const source = state.sources.find((s) => s.id === branch.source_id);
      if (source) card.append(ui().link(source.url, "Xem video nguồn đã chọn"));
      const buttons = ui().node("div", undefined, "toolbar"), process = Workspace.button("Xử lý video này", "process", {}, kind, branch.process_blockers.length > 0);
      process.title = branch.process_blockers.join(" · ");
      buttons.append(process, Workspace.button(branch.hold ? "Bỏ giữ" : "Giữ · không đăng", branch.hold ? "unhold" : "hold", {}, kind));
      buttons.append(Workspace.button("Làm lại bằng revision mới", "revise", {}, kind));
      const publish = ui().node("button", "Đăng ngay"); publish.disabled = true; publish.title = branch.release_blockers.join(" · ");
      buttons.append(publish); card.append(buttons);
      card.append(reasonList("Còn thiếu trước xử lý", branch.process_blockers), reasonList("Còn thiếu trước đăng", branch.release_blockers), copyForm(branch));
      if (kind === "created" && branch.scenes) card.append(scriptForm(branch));
      const previous = branch.history?.filter((v) => v.artifact).at(-1);
      if (previous) {
        const details = ui().node("details"), video = ui().node("video"); video.controls = true; video.preload = "none";
        video.src = `/api/content/media/${batch.id}/${kind}/${previous.revision}`;
        details.append(ui().node("summary", `So sánh bản trước · revision ${previous.revision}`), video); card.append(details);
      }
      outputs.append(card);
    }
    if (!processing.children.length) processing.append(ui().node("p", "Hiện không có video đang dựng. Không hiển thị tiến độ giả."));
  }
  function reasonList(title, reasons) {
    const wrap = ui().node("div", undefined, "reasons");
    if (reasons.length) wrap.append(ui().node("strong", title), ...reasons.map((r) => ui().node("p", r))); return wrap;
  }
  function publicationPreview(batch, branch) {
    const root = ui().node("details", undefined, "publication-preview");
    root.append(ui().node("summary", "Preview nội dung bài đăng"));
    const post = ui().node("article", undefined, "post-copy-preview");
    post.append(ui().node("p", batch.product.account, "muted"), ui().node("h3", branch.copy.title),
      ui().node("p", branch.copy.description), ui().node("p", branch.copy.hashtags.join(" "), "hashtags"));
    post.append(ui().link(batch.product.affiliate_url, "Mở link sản phẩm đã cấu hình"),
      ui().node("p", "Bản xem trước nội dung · chưa đăng. Shorts dẫn qua link hồ sơ, không nhấn URL trong chữ/video.", "muted"));
    root.append(post); return root;
  }
  function manualPackage(batch, branch) {
    const details = ui().node("details"); details.append(ui().node("summary", "Gói đăng tay · nội dung và đường link"));
    const text = ui().node("textarea"); text.readOnly = true; text.rows = 7;
    text.value = `${branch.copy.title}\n\n${branch.copy.description}\n${branch.copy.hashtags.join(" ")}\n\nTài khoản: ${batch.product.account}\nLink sản phẩm: ${batch.product.affiliate_url}\nVị trí cho Shorts: link hồ sơ kênh; đối chiếu link/SKU và xem/nghe trước khi đăng.`;
    text.setAttribute("aria-label", "Gói nội dung đăng tay");
    details.append(text, ui().node("p", "Tải MP4 không có nghĩa đã đăng. Không nhúng nút/link giả vào hình video.", "muted")); return details;
  }
  function copyForm(branch) {
    const form = ui().node("form", undefined, "panel-form");
    const [t, title] = Workspace.field("Tiêu đề đăng", branch.copy.title);
    const [d, description] = Workspace.field("Mô tả ngắn", branch.copy.description, true);
    const [h, hashtags] = Workspace.field("Hashtag", branch.copy.hashtags.join(" "));
    form.append(t, d, h, ui().node("button", "Lưu nội dung đăng"));
    form.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("copy", {title: title.value, description: description.value, hashtags: hashtags.value}, branch.kind, undefined, form);}); return form;
  }
  function scriptForm(branch) {
    const details = ui().node("details"), form = ui().node("form", undefined, "panel-form"), fields = [];
    details.append(ui().node("summary", "Sửa lời đọc và chữ · 5 cảnh tự tạo"));
    for (const [i, scene] of branch.scenes.entries()) {
      const row = {};
      for (const [key, name] of [["headline", "Tiêu đề cảnh"], ["label", "Chữ phụ"], ["voice", "Lời đọc"]]) {
        const [wrap, input] = Workspace.field(`Cảnh ${i + 1} · ${name}`, scene[key], key !== "label"); form.append(wrap); row[key] = input;
      }
      fields.push(row);
    }
    form.append(ui().node("button", "Lưu kịch bản · tạo revision mới"));
    form.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("script", {scenes: fields.map((row) => Object.fromEntries(Object.entries(row).map(([k, field]) => [k, field.value])))}, "created", undefined, form);});
    details.append(form); return details;
  }
  return {draw};
})();
