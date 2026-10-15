import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

player_path = "/s/player/0229cd64/tv-player-ias.vflset/tv-player-ias.js"
url = f"https://www.youtube.com{player_path}"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
print("Fetching tv-player-ias.js...")
js = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
print(f"tv-player-ias.js size: {len(js)} bytes")

keywords = ['adPlacements', 'adSlots', 'playerAds', 'adBreak', 'isAd', 'skipAd', 'videoAd', 'ad-showing']
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), js, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")
    for idx in matches[:2]:
        snippet = js[max(0, idx - 50):min(len(js), idx + 80)]
        print(f"   [{kw}] ...{snippet}...")
