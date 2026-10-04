const AffiliateView = (() => {
  function draw(state) {
    const ui = Workspace.ui(), root = document.getElementById("affiliate-stats"); root.replaceChildren();
    const latest = state.affiliate_reports.at(-1), cards = ui.node("div",undefined,"metrics affiliate-metrics");
    for (const [name,key] of [["Click theo báo cáo","clicks"],["Tổng đơn ghi nhận","total_orders"],["Hoa hồng ước tính","estimated_commission"],
      ["Đơn chờ duyệt","pending_orders"],["Hoa hồng được duyệt","approved_commission"],["Tiền đã thanh toán","paid_amount"]]) {
      const card = ui.node("article"); card.append(ui.node("p",name),ui.node("h2",ResultsView.metric(latest?.[key],key.includes("commission") || key === "paid_amount" ? " ₫" : ""))); cards.append(card);
    }
    root.append(cards,ui.node("p",latest ? "Số liệu nhập/đối chiếu từ báo cáo · chưa xác minh API. Kỳ " + latest.period_start + " → " + latest.period_end + " · " +
      (latest.product_id ? "riêng sản phẩm đã chọn" : "toàn tài khoản, không chia cho từng video") : "Chưa có báo cáo Shopee. Không dùng tổng lượt xem để suy ra hoa hồng.","data-status"));
    const list = ui.node("div",undefined,"report-list");
    for (const r of [...state.affiliate_reports].reverse()) {
      const product = state.products.find((p)=>p.id === r.product_id), card = ui.node("article",undefined,"report-card");
      card.append(ui.node("h3",product?.title || "Toàn tài khoản"),ui.node("p",r.period_start + " → " + r.period_end + " · " + r.report_reference),
        ui.node("p","Click " + ResultsView.metric(r.clicks) + " · Tổng đơn " + ResultsView.metric(r.total_orders) + " · Đơn chờ " + ResultsView.metric(r.pending_orders) + " · Đơn duyệt " + ResultsView.metric(r.approved_orders)),
        ui.node("p","Hoa hồng ước tính " + ResultsView.metric(r.estimated_commission," ₫")),
        ui.node("p","Hoa hồng chờ " + ResultsView.metric(r.pending_commission," ₫") + " · Hoa hồng duyệt " + ResultsView.metric(r.approved_commission," ₫") + " · Đã trả " + ResultsView.metric(r.paid_amount," ₫")),
        ui.node("p","Quan sát/nhập báo cáo · " + ui.date(r.observed_at),"muted")); list.append(card);
    }
    root.append(list,reportForm(state),ui.link("https://affiliate.shopee.vn/","Mở báo cáo Shopee Affiliate"));
  }
  function reportForm(state) {
    const ui = Workspace.ui(), details = ui.node("details"), form = ui.node("form",undefined,"panel-form form-grid"), fields = {};
    details.append(ui.node("summary","Nhập số liệu từ báo cáo Shopee của bạn"));
    const label = ui.node("label","Phạm vi báo cáo"), select = ui.node("select");
    select.append(new Option("Toàn tài khoản · không gán từng video",""),...state.products.map((p)=>new Option(p.title,p.id)));
    select.addEventListener("change",Workspace.markDirty); label.append(select); form.append(label);
    for (const [key,name,type] of [["period_start","Từ ngày","date"],["period_end","Đến ngày","date"],["report_reference","Tên/nguồn báo cáo","text"],
      ["clicks","Click","number"],["total_orders","Tổng đơn ghi nhận","number"],["estimated_commission","Hoa hồng ước tính · VND","number"],
      ["pending_orders","Đơn chờ duyệt","number"],["approved_orders","Đơn được duyệt","number"],
      ["pending_commission","Hoa hồng chờ · VND","number"],["approved_commission","Hoa hồng duyệt · VND","number"],["paid_amount","Tiền đã trả · VND","number"]]) {
      const [wrap,input] = Workspace.field(name,""); input.type = type; input.required = type !== "number"; if (type === "number") {input.min = 0; input.step = key.includes("orders") || key === "clicks" ? 1 : "any";}
      fields[key] = input; form.append(wrap);
    }
    form.append(ui.node("p","Để trống chỉ số chưa có dữ liệu. Cùng sản phẩm/kỳ sẽ cập nhật, không cộng trùng các kỳ chồng nhau.","muted"),ui.node("button","Lưu báo cáo của chủ"));
    form.addEventListener("submit",(e)=>{e.preventDefault();const data = {product_id:select.value};
      for (const [key,input] of Object.entries(fields)) data[key] = input.type === "number" ? input.value === "" ? null : Number(input.value) : input.value;
      Workspace.command("affiliate_report",data,undefined,undefined,form);}); details.append(form); return details;
  }
  return {draw};
})();
