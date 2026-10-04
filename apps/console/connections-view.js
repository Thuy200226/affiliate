const ConnectionsView = (() => {
  async function draw() {
    const ui = Workspace.ui(), root = document.getElementById("tool-settings");
    try {
      const data = await ui.request("/api/connections"); root.replaceChildren();
      for (const tool of data.tools) {
        const card = ui.node("article",undefined,"connection-card"); card.append(ui.node("h3",tool.title),ui.node("p",tool.help),
          ui.node("p",(tool.key_saved ? "Đã lưu trong Keychain · " + ui.date(tool.saved_at) : "Chưa lưu key/token") + " · quyền API chưa được kiểm chứng","link-state"),
          ui.node("p",tool.session_status,"muted"));
        const login = ui.node("button","Mở Chrome · đăng nhập / giữ phiên", "secondary"); login.disabled = !tool.chrome_available;
        login.addEventListener("click",()=>Workspace.endpoint("/api/connections/open",{tool:tool.id}));
        card.append(login,ui.link(tool.url,"Mở trang công cụ trong trình duyệt hiện tại"));
        if (tool.id !== "flow") card.append(keyForm(tool));
        if (tool.id === "youtube") card.append(ui.link("http://localhost:5678/home/credentials","Đăng nhập lại OAuth YouTube trong n8n"));
        root.append(card);
      }
    } catch(error) {ui.notice(error.message,true);}
  }
  function keyForm(tool) {
    const ui = Workspace.ui(), details = ui.node("details"), form = ui.node("form",undefined,"panel-form");
    details.append(ui.node("summary","Gắn / thay key hoặc token")); const [wrap,input] = Workspace.field("Key/token mới · không hiển thị lại","");
    input.type = "password"; input.autocomplete = "new-password"; input.required = true;
    form.append(wrap,ui.node("button","Lưu trong Keychain"));
    form.addEventListener("submit",async(e)=>{e.preventDefault();if (await Workspace.endpoint("/api/connections/save",{tool:tool.id,value:input.value},form)) {input.value = ""; draw();}});
    details.append(form);
    if (tool.key_saved) {
      const remove = ui.node("button","Gỡ key đã lưu", "secondary"); remove.addEventListener("click",async()=>{if (await Workspace.endpoint("/api/connections/remove",{tool:tool.id})) draw();}); details.append(remove);
    }
    details.append(ui.node("p","Lưu key không đồng nghĩa kết nối đang hoạt động. Không bật trả phí hoặc xuất cookie/phiên vào Git.","muted")); return details;
  }
  return {draw};
})();
