const CatalogView = (() => {
  const categories = {technology:"Công nghệ", fashion:"Thời trang", home:"Nhà cửa", beauty:"Làm đẹp", sports:"Thể thao", other:"Khác"};
  const platforms = {youtube_shorts:"YouTube Shorts · link hồ sơ", youtube_long:"YouTube dài · mô tả", tiktok:"TikTok · hồ sơ", instagram_reels:"Instagram Reels · hồ sơ", facebook_post:"Facebook · nội dung bài"};
  const ui = () => Workspace.ui();
  let filter = "", query = "";
  function draw(state, selected) {
    const root = document.getElementById("catalog-list"); root.replaceChildren();
    const bar = ui().node("div", undefined, "toolbar"), category = ui().node("select"), search = ui().node("input");
    category.setAttribute("aria-label", "Lọc nhóm hàng"); search.setAttribute("aria-label", "Tìm trong sản phẩm đã tổng hợp");
    category.append(new Option("Tất cả nhóm hàng", ""), ...Object.entries(categories).map(([v,t]) => new Option(t,v)));
    category.value = filter; search.placeholder = "Tìm sản phẩm, mã Item hoặc nhóm hàng…"; search.value = query;
    const paint = () => {filter = category.value; query = search.value; filterCards(root);};
    category.addEventListener("change", paint); search.addEventListener("input", paint); bar.append(category, search); root.append(bar);
    const list = ui().node("div", undefined, "product-grid");
    const products = [...state.products].sort((a,b) => Number(b.priority === "first") - Number(a.priority === "first"));
    for (const p of products) {
      const card = ui().node("article", undefined, "product-card" + (p.id === selected?.id ? " chosen" : ""));
      card.dataset.category = p.category; card.dataset.search = `${p.title} ${p.item_id} ${categories[p.category]}`.toLowerCase();
      if (p.image_url) {const image = ui().node("img"); image.src = p.image_url; image.alt = p.title; image.loading = "lazy"; card.append(image);}
      card.append(ui().node("p", `${categories[p.category]} · ${p.status === "skipped" ? "ĐÃ BỎ QUA" : p.priority === "first" ? "LÀM TRƯỚC" : "SẴN TRONG DANH MỤC"}`, "pill"),
        ui().node("h3",p.title), ui().node("p",p.summary), ui().node("p",`Shop ${p.shop_id} · Item ${p.item_id}\n${p.variant}`,"muted"),
        ui().link(`https://shopee.vn/product/${p.shop_id}/${p.item_id}`,"Mở đúng trang sản phẩm"), ui().link(p.affiliate_url,"Mở link affiliate"),
        ui().node("p",p.link_check,"link-state"));
      const row = ui().node("div",undefined,"toolbar"), choose = ui().node("button",p.id === selected?.id ? "Đang xem sản phẩm" : "Xem nguồn & video", "secondary");
      choose.disabled = p.id === selected?.id; choose.addEventListener("click",()=>Workspace.selectProduct(p.id));
      row.append(choose, Workspace.button(p.priority === "first" ? "Bỏ ưu tiên" : "Làm trước", "product_choice",{product_id:p.id,choice:p.priority === "first" ? "normal" : "first"}),
        Workspace.button(p.status === "skipped" ? "Khôi phục" : "Bỏ qua", "product_choice",{product_id:p.id,choice:p.status === "skipped" ? "restore" : "skip"}),
        Workspace.button("Tạo 2 video sản phẩm này", "batch",{product_id:p.id},undefined,p.status === "skipped"));
      card.append(row, editForm(p), bindingForm(p)); list.append(card);
    }
    const empty = ui().node("p", "Không có sản phẩm khớp bộ lọc. Đổi nhóm hàng/từ khoá, hoặc thêm sản phẩm bằng biểu mẫu bên dưới.", "catalog-empty data-status");
    empty.setAttribute("role", "status");
    root.append(list, empty, ui().node("p", "Làm trước là lựa chọn của bạn, không phải đánh giá sản phẩm tối ưu nếu chưa có dữ liệu tương tác/đơn hàng.", "muted"), editForm());
    filterCards(root);
  }
  function filterCards(root) {
    root.querySelectorAll(".product-card").forEach((c)=>{c.hidden = (!!filter && c.dataset.category !== filter) || !c.dataset.search.includes(query.toLowerCase());});
    root.querySelector(".catalog-empty").hidden = !!root.querySelector(".product-card:not([hidden])");
  }
  function editForm(p = {}) {
    const details = ui().node("details"), form = ui().node("form",undefined,"panel-form form-grid"), fields = {};
    details.append(ui().node("summary",p.id ? "Sửa sản phẩm / link / từ khoá" : "＋ Thêm sản phẩm từ tài khoản affiliate của bạn"));
    for (const [key,label,multi] of [["title","Tên sản phẩm"],["summary","Nội dung sản phẩm đã đối chiếu",true],["shop_id","Shopee · Shop ID"],["item_id","Shopee · Item ID"],
      ["variant","Biến thể cụ thể"],["affiliate_url","Link affiliate do tài khoản bạn tạo"],["account","Tài khoản sẽ đăng"],["query","Từ khoá tìm video riêng sản phẩm"],["image_url","Ảnh sản phẩm · URL CDN Shopee"]]) {
      const [wrap,input] = Workspace.field(label,p[key],multi); fields[key] = input; form.append(wrap);
      input.required = !["summary","image_url","query"].includes(key);
    }
    for (const [key,label,values] of [["category","Nhóm hàng",categories],["platform","Nền tảng đích & vị trí link",platforms]]) {
      const wrap = ui().node("label",label), select = ui().node("select"); select.append(...Object.entries(values).map(([v,t])=>new Option(t,v)));
      select.value = p[key] || Object.keys(values)[0]; select.addEventListener("change",Workspace.markDirty); fields[key] = select; wrap.append(select); form.append(wrap);
    }
    form.append(ui().node("button",p.id ? "Lưu sản phẩm · không đổi batch cũ" : "Thêm vào danh mục"));
    form.addEventListener("submit",(e)=>{e.preventDefault();const data = Object.fromEntries(Object.entries(fields).map(([k,v])=>[k,v.value]));
      if (p.id) data.product_id = p.id; Workspace.command("product",data,undefined,undefined,form);}); details.append(form); return details;
  }
  function bindingForm(p) {
    const details = ui().node("details"), form = ui().node("form",undefined,"panel-form"); details.append(ui().node("summary","Đối chiếu link đúng sản phẩm và tài khoản"));
    const checks = [];
    for (const name of ["Tôi đã tạo link này trong tài khoản affiliate của mình", "Tôi đã mở link và đối chiếu đúng Shop/Item/biến thể nêu trên"]) {
      const label = ui().node("label",name), checkbox = ui().node("input"); checkbox.type = "checkbox"; checkbox.required = true;
      checkbox.addEventListener("change",Workspace.markDirty); label.prepend(checkbox); checks.push(checkbox); form.append(label);
    }
    form.append(ui().node("button","Lưu đối chiếu của chủ · hiệu lực 24 giờ"));
    form.addEventListener("submit",(e)=>{e.preventDefault();Workspace.command("link_verify",{product_id:p.id,affiliate_url:p.affiliate_url,shop_id:p.shop_id,item_id:p.item_id,variant:p.variant,account:p.account,
      owner_generated:checks[0].checked,destination_checked:checks[1].checked},undefined,undefined,form);}); details.append(form); return details;
  }
  return {draw};
})();
