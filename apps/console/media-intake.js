const MediaIntake = (() => {
  function local(url, label) {
    const ui = Workspace.ui(), wrap = ui.node("div",undefined,"local-preview"), video = ui.node("video");
    video.controls = true; video.preload = "metadata"; video.src = url; video.setAttribute("aria-label",label);
    wrap.append(ui.node("p",label,"muted"),video); return wrap;
  }
  function form(state, target, ident) {
    const ui = Workspace.ui(), details = ui.node("details"), form = ui.node("form",undefined,"panel-form");
    details.append(ui.node("summary",target === "source" ? "Nhận MP4 nguồn bạn đã tải hợp lệ" : "Nhận MP4 sau xử lý để so sánh"));
    const input = ui.node("input"), label = ui.node("label","Chọn MP4 trên máy · tối đa 100 MB / 180 giây");
    input.type = "file"; input.accept = "video/mp4,.mp4"; input.required = true; input.addEventListener("change",Workspace.markDirty); label.append(input);
    const button = ui.node("button","Gửi tệp và kiểm tra giải mã"); form.append(label,button);
    form.addEventListener("submit",async(e)=>{
      e.preventDefault(); const file = input.files[0];
      if (!file || file.size > 100 * 1024 * 1024) {ui.notice("Chọn MP4 tối đa 100 MB.",true); return;}
      button.disabled = true; button.textContent = "Đang gửi / kiểm tệp…";
      try {await Workspace.endpoint("/api/content/upload",file,form,{"Content-Type":"video/mp4", "X-Media-Target":target,"X-Media-Id":ident,"X-Workspace-Version":String(state.version)});}
      finally {button.disabled = false; button.textContent = "Gửi tệp và kiểm tra giải mã";}
    });
    details.append(form,ui.node("p", target === "source" ? "Danh sách nhận nguồn từ nhiều nơi. URL không có nghĩa đã tải được MP4; không tải vượt hạn chế nền tảng." :
      "Đây là nhận tệp đầu ra thật. Hệ thống chưa tự chạy Flow hoặc xác minh đổi mặt; xem và đối chiếu trước/sau ở đây.","muted")); return details;
  }
  return {local,form};
})();
