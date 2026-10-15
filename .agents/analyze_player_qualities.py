import urllib.request
import re
import os

url = "https://www.youtube.com/s/player/0229cd64/tv-player-ias.vflset/tv-player-ias.js"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

js_path = ".agents/tv-player-ias.js"
if not os.path.exists(js_path):
    print("Downloading tv-player-ias.js...")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    data = urllib.request.urlopen(req).read()
    with open(js_path, "wb") as f:
        f.write(data)
    print("Downloaded, size:", len(data))
else:
    print("Already exists, size:", os.path.getsize(js_path))

with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

# Search for quality levels: hd2160, hd1440, hd1080, hd720, etc.
keywords = ["hd2160", "hd1440", "hd1080", "hd720", "2160p", "1080p", "getAvailableQualityLevels", "getAvailableQualityData", "setPlaybackQualityRange", "maxResolution", "screen.height", "screen.width", "devicePixelRatio"]
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")
    for idx in matches[:3]:
        snippet = js[max(0, idx - 100):min(len(js), idx + 150)]
        print(f"  [{kw}] snippet: {snippet}\n")
