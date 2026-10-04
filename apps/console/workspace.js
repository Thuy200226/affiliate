const Workspace = (() => {
  let state = null, selected = "", productId = "", pending = false;
  const drafts = new Set();
  const ui = () => window.AffiliateUI;
  const current = () => state?.batches.find((b) => b.id === selected);
  const product = () => state?.products.find((p) => p.id === productId) || state?.products[0];
  async function refresh(force = false) {
    try {
      const data = await ui().request("/api/content");
      const playing = [...document.querySelectorAll("video")].some((v) => !v.paused);
      const editing = document.activeElement?.matches("input,textarea,select");
      const sourcePreview = document.querySelector("#sources iframe[data-preview]");
      if (!force && (drafts.size || playing || sourcePreview || editing || state?.version === data.version)) return;
      state = data;
      if (!productId) productId = current()?.product.id || state.products[0]?.id || "";
      if (!selected) selected = state.batches.filter((b) => b.product.id === productId).at(-1)?.id || "";
      const batch = current();
      document.getElementById("batch-select").replaceChildren(...state.batches.map((b) => {
        const option = ui().node("option", `${b.product.title} · ${ui().date(b.created_at)}`);
        option.value = b.id; option.selected = b.id === selected; return option;
      }));
      const counts = state.batches.flatMap((b) => Object.values(b.branches));
      document.getElementById("workspace-counts").textContent = `${state.sources.length} nguồn · ${counts.filter((b) => b.status === "processing").length} đang dựng · ${counts.filter((b) => b.status === "ready").length} bản đã dựng`;
      CatalogView.draw(state, product()); SourceView.draw(state, batch, product());
      OutputView.draw(state, batch); SettingsView.draw(state); AffiliateView.draw(state);
    } catch (error) { ui().notice(error.message, true); }
  }
  async function command(action, data = {}, kind, batchId, savedForm) {
    if (pending || !state) return;
    const others = [...drafts].some((form) => form !== savedForm);
    if (others && !await askDiscard("Có biểu mẫu khác chưa lưu. Bỏ nội dung ở biểu mẫu đó để thực hiện thao tác này?")) return;
    pending = true;
    const body = {action, data, expected_version: state.version, idempotency_key: crypto.randomUUID()};
    if (kind) body.kind = kind;
    if (batchId || current()) body.batch_id = batchId || current().id;
    try {
      const result = await ui().request("/api/content/commands", {method: "POST", headers: {
        "Content-Type": "application/json", "X-CSRF-Token": ui().csrf()}, body: JSON.stringify(body)});
      if (action === "batch") {selected = result.batch_id; productId = data.product_id;}
      if (action === "product") {productId = result.product_id; selected = "";}
      drafts.clear();
      ui().notice(action === "process" ? "Đã nhận yêu cầu dựng thật. Xem bước hiện tại ở Đang xử lý." : "Đã lưu thay đổi.");
      await refresh(true);
      window.AffiliateUI.refreshOverview?.();
    } catch (error) {ui().notice(error.message + " Nội dung đang nhập vẫn được giữ.", true);}
    finally {pending = false;}
  }
  async function selectProduct(ident) {
    if (drafts.size && !await askDiscard("Có nội dung chưa lưu. Bỏ nội dung đang nhập để chọn sản phẩm khác?")) return;
    productId = ident; selected = state.batches.filter((b) => b.product.id === ident).at(-1)?.id || "";
    drafts.clear(); await refresh(true);
  }
  async function endpoint(path, body, form, headers = {}) {
    if (pending) return false;
    if ([...drafts].some((f) => f !== form) && !await askDiscard("Bỏ nội dung chưa lưu ở biểu mẫu khác để tiếp tục?")) return false;
    pending = true;
    try {
      await ui().request(path, {method:"POST", headers:{"Content-Type":"application/json", "X-CSRF-Token":ui().csrf(), ...headers},
        body:body instanceof Blob ? body : JSON.stringify(body)});
      drafts.clear(); ui().notice("Đã lưu/nhận kết quả. Trạng thái chưa kiểm chứng vẫn được ghi rõ.");
      await refresh(true); return true;
    } catch(error) {ui().notice(error.message, true); return false;}
    finally {pending = false;}
  }
  function button(label, action, data = {}, kind, disabled = false) {
    const b = ui().node("button", label, "secondary"); b.type = "button"; b.disabled = disabled;
    b.addEventListener("click", () => command(action, data, kind)); return b;
  }
  function field(label, value, multi = false) {
    const wrap = ui().node("label", label), input = ui().node(multi ? "textarea" : "input");
    input.value = value || ""; input.addEventListener("input", markDirty);
    wrap.append(input); return [wrap, input];
  }
  function markDirty(event) {drafts.add(event.target.closest("form") || event.target);}
  function askDiscard(message) {
    if (document.getElementById("discard-prompt")) return Promise.resolve(false);
    return new Promise((resolve) => {
      const panel = ui().node("section", undefined, "discard-prompt"); panel.id = "discard-prompt";
      panel.setAttribute("role", "alertdialog"); panel.setAttribute("aria-modal", "true");
      const heading = ui().node("h3", "Nội dung chưa lưu"); heading.id = "discard-heading";
      panel.setAttribute("aria-labelledby", heading.id);
      const description = ui().node("p", message); description.id = "discard-description";
      panel.setAttribute("aria-describedby", description.id);
      const cancel = ui().node("button", "Giữ nội dung đang sửa", "secondary");
      const proceed = ui().node("button", "Bỏ nội dung chưa lưu · tiếp tục");
      const before = document.activeElement;
      const background = [...document.querySelectorAll("body>main,body>aside")].map((element) => [element, element.inert]);
      background.forEach(([element]) => {element.inert = true;});
      const close = (answer) => {
        panel.remove(); document.removeEventListener("keydown", keyboard);
        background.forEach(([element, prior]) => {element.inert = prior;}); before?.focus(); resolve(answer);
      };
      const keyboard = (event) => {
        if (event.key === "Escape") close(false);
        if (event.key === "Tab") {
          event.preventDefault();
          (document.activeElement === cancel ? proceed : cancel).focus();
        }
      };
      cancel.addEventListener("click", () => close(false)); proceed.addEventListener("click", () => close(true));
      panel.append(heading, description, cancel, proceed);
      document.body.append(panel); document.addEventListener("keydown", keyboard); cancel.focus();
    });
  }
  async function start() {
    await refresh(true);
    document.getElementById("batch-select").addEventListener("change", async (e) => {
      if (drafts.size && !await askDiscard("Có nội dung chưa lưu. Bỏ nội dung đang nhập và đổi batch?")) {e.target.value = selected; return;}
      selected = e.target.value; drafts.clear(); refresh(true);
      productId = current()?.product.id || productId;
    });
    document.getElementById("refresh-workspace").addEventListener("click", async () => {
      if (drafts.size && !await askDiscard("Đọc lại trạng thái sẽ bỏ nội dung chưa lưu. Tiếp tục?")) return;
      drafts.clear(); refresh(true);
    });
    document.getElementById("new-batch").addEventListener("click", () => {
      if (product()) command("batch", {product_id: product().id});
      else ui().notice("Chưa có sản phẩm được cấu hình.", true);
    });
    setInterval(() => refresh(), 5000);
  }
  return {refresh, command, button, field, current, product, selectProduct, endpoint, start, ui, markDirty,
    snapshot:() => state, hasDrafts:() => drafts.size > 0};
})();
document.addEventListener("affiliate-ready", () => Workspace.start(), {once: true});
