const SettingsView = (() => {
  function draw(state) {
    const ui = Workspace.ui(), root = document.getElementById("search-settings"); root.replaceChildren();
    const form = ui.node("form", undefined, "panel-form");
    const [q, query] = Workspace.field("Từ khoá tìm kiếm nguyên văn", state.settings.query); query.maxLength = 250;
    const order = ui.node("select"), mode = ui.node("select"), limit = ui.node("input");
    [order, mode, limit].forEach((field) => field.addEventListener("change", Workspace.markDirty));
    for (const [value, name] of [["relevance", "Theo kết quả phù hợp của YouTube"], ["date", "Mới đăng"], ["viewCount", "Tổng lượt xem · không phải tốc độ tăng"]]) {
      const option = ui.node("option", name); option.value = value; option.selected = state.settings.order === value; order.append(option);
    }
    for (const [value, name] of [["per_source", "Xác nhận từng nguồn"], ["reuse_valid", "Bỏ hỏi lại nguồn đã xác nhận còn hiệu lực"]]) {
      const option = ui.node("option", name); option.value = value; option.selected = state.settings.confirmation_mode === value; mode.append(option);
    }
    const o = ui.node("label", "Thứ tự tìm kiếm"), m = ui.node("label", "Xác nhận nguồn"), l = ui.node("label", "Số video / lần tìm");
    o.append(order); m.append(mode); limit.type = "number"; limit.min = 1; limit.max = 25; limit.value = state.settings.limit; l.append(limit);
    form.append(q, o, l, m, ui.node("button", "Lưu cấu hình"));
    form.addEventListener("submit", (e) => {e.preventDefault(); Workspace.command("settings", {
      query: query.value, order: order.value, limit: Number(limit.value), confirmation_mode: mode.value}, undefined, undefined, form);});
    root.append(form, ui.node("p", "Hai nhánh mặc định hướng tới auto, nhưng lịch công khai chưa bật: phải nối publisher/link và kiểm thử trước. Không có nút giả bật lịch.", "muted"));
    const connections = ui.node("div", undefined, "toolbar");
    connections.append(ui.link("http://localhost:5678/home/credentials", "Mở kết nối n8n để đăng nhập lại"), ui.link("https://studio.youtube.com/", "Mở YouTube Studio"),
      ui.link("https://affiliate.shopee.vn/", "Mở Shopee Affiliate"), ui.link("https://labs.google/fx/tools/flow", "Mở Google Flow"));
    root.append(connections, ui.node("p", `Tìm kiếm API: ${state.capabilities.video_search ? "đã cấu hình" : "chưa có kết nối tìm kiếm"}. Đăng nhập web không tự cấp quyền API; không lưu cookie hoặc key vào Git.`, "muted"));
  }
  return {draw};
})();
