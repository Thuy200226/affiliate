"""Fixed official endpoint; no scraping, cookie extraction or rights search filter."""
import html
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def configured():
    return bool(os.environ.get("AFFILIATE_YOUTUBE_API_KEY"))


def search(profile):
    key = os.environ.get("AFFILIATE_YOUTUBE_API_KEY")
    if not key:
        raise ValueError("Chưa cấu hình kết nối tìm kiếm YouTube; có thể mở tìm kiếm web và thêm URL nguồn.")
    query = urlencode({"part": "snippet", "type": "video", "q": profile["query"],
                       "maxResults": profile["limit"], "order": profile["order"],
                       "regionCode": "VN", "key": key})
    request = Request("https://www.googleapis.com/youtube/v3/search?" + query)
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("Kết quả tìm kiếm vượt giới hạn.")
            data = json.loads(raw)
    except (HTTPError, URLError):
        raise ValueError("YouTube từ chối hoặc chưa kết nối được; kiểm API/quota. Không ghi key vào log.") from None
    return [{"url": "https://www.youtube.com/watch?v=" + item["id"]["videoId"],
             "title": html.unescape(item["snippet"]["title"]),
             "creator": html.unescape(item["snippet"]["channelTitle"]),
             "published_at": item["snippet"].get("publishedAt"),
             "method": "youtube_data_api", "query": profile["query"]}
            for item in data.get("items", []) if item.get("id", {}).get("videoId")]
