const SourceView = (() => {
  const ui = () => Workspace.ui();
  function draw(state, batch, product) {
    const root = document.getElementById("sources"); root.replaceChildren();
    if (!product) {root.append(ui().node("p", "Chưa nối catalog sản phẩm.")); return;}
    root.append(ui().node("h3", product.title), ui().node("p", product.summary), ui().link(product.affiliate_url, "Link affiliate đã cấu hình"));
    root.append(ui().node("p", `Biến thể: ${product.variant} · Đích: ${product.account} · Link cần đối chiếu mới trước đăng.`, "muted"));
    const row = ui().node("div", undefined, "toolbar");
    const query = encodeURIComponent(product.query || state.settings.query);
    row.append(ui().link("https://www.youtube.com/results?search_query=" + query, "Tìm YouTube"),
      ui().link("https://www.tiktok.com/search/video?q=" + query, "Tìm TikTok"),
      ui().link("https://www.google.com/search?q=" + encodeURIComponent(`site:instagram.com/reel ${product.query || product.title}`), "Tìm Instagram"),
      ui().link("https://www.google.com/search?q=" + query, "Tìm nguồn khác"));
    const search = Workspace.button("Tìm qua kết nối YouTube", "search", {product_id: product.id}, undefined, !state.capabilities.video_search);
    search.title = state.capabilities.video_search ? "Đọc API chính thức" : "Chưa cấu hình kết nối tìm kiếm";
    row.append(search); root.append(row);
    root.append(ui().node("p", "Danh sách không lọc theo quyền. Bạn chọn nguồn, rồi xác nhận ở bước riêng. Chưa có số liệu không được chấm là video hấp dẫn nhất.", "muted"));
    const sources = state.sources.filter((s) => s.product_id === product.id), list = ui().node("div", undefined, "source-grid");
    for (const source of sources) {
      const chosen = batch?.branches.selected.source_id === source.id;
      const card = ui().node("article", undefined, chosen ? "source-card chosen" : "source-card");
      card.append(MediaPreview.create(source.url, source.title));
      card.append(ui().link(source.url, source.title), ui().node("p", source.creator));
      card.append(ui().node("p", `${chosen ? "ĐÃ CHỌN · " : ""}${source.method === "youtube_data_api" ? "API YouTube" : "Nhập từ web · metadata cần đối chiếu"} · ${ui().date(source.observed_at)}`, "muted"));
      card.append(ui().node("p", `${source.provider || "Nguồn web"} · ${source.asset ? "Đã nhận MP4 · kiểm kỹ thuật đạt" : "Chưa nhận tệp MP4"}`, "source-status"));
      if (source.asset) card.append(MediaIntake.local(`/api/content/source-media/${source.id}`, "Video nguồn đã nhận"));
      card.append(MediaIntake.form(state, "source", source.id));
      card.append(Workspace.button(chosen ? "Đang chọn" : "Chọn cho video 2", "select", {source_id: source.id}, "selected", !batch || chosen)); list.append(card);
    }
    if (!sources.length) list.append(ui().node("p", "Chưa có nguồn. Mở tìm kiếm và thêm URL, hoặc cấu hình kết nối tìm kiếm tự động."));
    root.append(list, importForm(product));
    if (batch && batch.product.id === product.id) root.append(ui().node("p",`Batch ${batch.id.slice(0,8)} đang dùng snapshot sản phẩm lúc tạo. Đổi SKU/link ở danh mục không sửa lịch sử batch này.`,"muted"));
    if (batch?.branches.selected.source_id) root.append(confirmation(batch.branches.selected));
  }
  function importForm(product) {
    const form = ui().node("form", undefined, "panel-form");
    const [u, url] = Workspace.field("URL video · YouTube / TikTok / Instagram / Facebook / nguồn web khác", ""); url.required = true; url.type = "url";
    const [t, title] = Workspace.field("Tên video", ""); title.required = true; title.maxLength = 180;
    const [c, creator] = Workspace.field("Người đăng / nguồn", ""); creator.maxLength = 120;
    form.append(u, t, c, ui().node("button", "Thêm vào danh sách"));
    form.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("source", {
      product_id: product.id, url: url.value, title: title.value, creator: creator.value || "Chưa biết"}, undefined, undefined, form);}); return form;
  }
  function confirmation(branch) {
    const details = ui().node("details"), form = ui().node("form", undefined, "panel-form");
    details.append(ui().node("summary", "Xác nhận nguồn đã chọn và yêu cầu xử lý"));
    const media = ui().node("input"), person = ui().node("input"); media.type = person.type = "checkbox";
    [media, person].forEach((field) => field.addEventListener("change", Workspace.markDirty));
    const m = ui().node("label", "Tôi xác nhận được dùng media và âm thanh của nguồn này"); m.prepend(media);
    const p = ui().node("label", "Có đồng ý chỉnh hình người xuất hiện nếu yêu cầu edit người"); p.prepend(person);
    if (branch.confirmation) form.append(ui().node("p", `Đã lưu xác nhận tới ${ui().date(branch.confirmation.expires_at)}. Tệp MP4 thực tế còn phải đối chiếu.`, "muted"));
    form.append(m, p, ui().node("button", "Lưu xác nhận nguồn"));
    form.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("confirm", {media_audio: media.checked, person_edit: person.checked}, "selected", undefined, form);});
    const [wrap, request] = Workspace.field("Yêu cầu chỉnh nguồn / nhân vật thay thế", branch.edit_request, true);
    const editForm = ui().node("form", undefined, "panel-form");
    editForm.append(wrap, ui().node("button", "Lưu yêu cầu edit"));
    editForm.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("edit", {request: request.value}, "selected", undefined, editForm);});
    details.append(form, editForm); return details;
  }
  return {draw};
})();
