const PostActions = (() => {
  function create(video) {
    const ui = window.AffiliateUI, controls = video.control || {}, root = ui.node("details",undefined,"post-tools");
    root.append(ui.node("summary","Quản lý bài · sản phẩm / ẩn / xoá"));
    root.append(Workspace.button(controls.hidden ? "Hiện lại trong bảng" : "Ẩn khỏi bảng · không xoá trên YouTube", "post_control",{video_id:video.video_id,choice:controls.hidden ? "restore" : "hide"}));
    const form = ui.node("form",undefined,"panel-form"), select = ui.node("select"), wrap = ui.node("label","Đối chiếu bài này với sản phẩm");
    select.append(new Option("Chọn sản phẩm đã tổng hợp…",""),...(Workspace.snapshot()?.products || []).map((p)=>new Option(p.title + " · " + p.item_id,p.id)));
    select.value = controls.product_id || ""; select.required = true; select.addEventListener("change",Workspace.markDirty); wrap.append(select);
    form.append(wrap,ui.node("button","Lưu mapping bài → sản phẩm"));
    form.addEventListener("submit",(e)=>{e.preventDefault();Workspace.command("post_control",{video_id:video.video_id,choice:"bind",product_id:select.value},undefined,undefined,form);}); root.append(form);
    const deletion = ui.node("form",undefined,"panel-form"), [idWrap,input] = Workspace.field("Gõ ID video để xác nhận yêu cầu xoá","");
    input.placeholder = video.video_id; input.required = true;
    deletion.append(ui.node("p","Xoá trên YouTube là vĩnh viễn. ID: " + video.video_id + ". Nút yêu cầu chỉ ghi nhận, chưa xoá.","muted"),idWrap,ui.node("button","Ghi nhận yêu cầu xoá", "danger"));
    deletion.addEventListener("submit",(e)=>{e.preventDefault();Workspace.command("post_control",{video_id:video.video_id,confirm_id:input.value,choice:"request_delete"},undefined,undefined,deletion);}); root.append(deletion);
    const labels = {requested_not_deleted:"Đang yêu cầu · CHƯA XOÁ", deleting:"Đang xoá · chờ kết quả",uncertain:"Chưa rõ kết quả · không thử xoá lại mù",
      deleted_on_youtube:"ĐÃ XOÁ trên YouTube · không thể phục hồi",cancelled:"Đã huỷ yêu cầu"};
    if (controls.deletion) root.append(ui.node("p",labels[controls.deletion] || controls.deletion,"data-status"));
    if (controls.deletion === "requested_not_deleted") root.append(finalForm(video));
    return root;
  }
  function finalForm(video) {
    const ui = window.AffiliateUI, root = ui.node("div");
    root.append(Workspace.button("Huỷ yêu cầu xoá","post_control",{video_id:video.video_id,choice:"cancel_delete"}),ui.link("https://studio.youtube.com/","Mở Studio để xoá bằng tài khoản chủ"));
    const form = ui.node("form",undefined,"panel-form"), [wrap,input] = Workspace.field("Xác nhận lần cuối · gõ lại ID", ""); input.required = true;
    form.append(wrap,ui.node("p","Cần OAuth YouTube của đúng kênh có quyền xoá trong Settings. Không khôi phục được lượt xem/bình luận.","muted"),ui.node("button","XOÁ VĨNH VIỄN qua YouTube", "danger"));
    form.addEventListener("submit",async(e)=>{e.preventDefault();if (input.value !== video.video_id) {ui.notice("ID không khớp; chưa xoá.",true);return;}
      await Workspace.endpoint("/api/posts/delete",{video_id:video.video_id,confirm_id:input.value,permanent:true,expected_version:Workspace.snapshot().version,idempotency_key:crypto.randomUUID()},form);
      ui.refreshOverview?.();}); root.append(form); return root;
  }
  return {create};
})();
