const MediaPreview = (() => {
  function youtubeId(value) {
    try {
      const url = new URL(value);
      if (url.protocol !== "https:" || url.username || url.password || (url.port && url.port !== "443")) return null;
      if (!["youtube.com", "www.youtube.com", "youtu.be"].includes(url.hostname)) return null;
      const id = url.hostname === "youtu.be" ? url.pathname.slice(1) :
        url.pathname.startsWith("/shorts/") ? url.pathname.split("/")[2] : url.searchParams.get("v");
      return /^[A-Za-z0-9_-]{11}$/.test(id || "") ? id : null;
    } catch {return null;}
  }
  function create(url, title, publicVideo = true) {
    const ui = window.AffiliateUI, id = youtubeId(url), root = ui.node("div", undefined, "media-preview");
    if (!id || !publicVideo) {
      root.append(ui.node("p", publicVideo ? "Xem video trên nền tảng nguồn." : "Chưa công khai · mở bằng tài khoản chủ.", "empty-preview"));
      root.append(ui.link(url, "Mở video gốc")); return root;
    }
    const image = ui.node("img"); image.src = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
    image.alt = `Ảnh xem trước: ${title}`; image.loading = "lazy"; image.referrerPolicy = "no-referrer";
    image.addEventListener("error", () => {image.replaceWith(ui.node("p", "Thumbnail chưa tải được · vẫn có thể mở video.", "empty-preview"));});
    const details = ui.node("details"), player = ui.node("div", undefined, "embedded-player");
    details.append(ui.node("summary", "Xem preview ngay tại đây"), player);
    details.addEventListener("toggle", () => {
      player.replaceChildren();
      if (!details.open) return;
      const iframe = ui.node("iframe"); iframe.title = `Video: ${title}`;
      iframe.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=0&controls=1&playsinline=1`;
      iframe.referrerPolicy = "strict-origin-when-cross-origin"; iframe.allowFullscreen = true;
      iframe.allow = "encrypted-media; fullscreen; picture-in-picture"; iframe.dataset.preview = "true";
      player.append(iframe, ui.node("p", "Preview từ YouTube. Nếu nền tảng không cho nhúng, chọn Mở video gốc.", "muted"), ui.link(url, "Mở video gốc"));
    });
    root.append(image, details); return root;
  }
  return {youtubeId, create};
})();
if (typeof module !== "undefined") module.exports = MediaPreview;
