import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

player_path = "/s/player/0229cd64/tv-player-ias.vflset/tv-player-ias.js"
url = f"https://www.youtube.com{player_path}"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

js = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

# Search for inline styles or controls classes injected by tv-player-ias.js
for m in re.finditer(r'(\.ytp-[^{}]*controls[^{}]*\{[^{}]*\})', js):
    print("Controls CSS:", m.group(1)[:200])

for m in re.finditer(r'(\.ytp-gradient-bottom[^{}]*\{[^{}]*\})', js):
    print("Gradient CSS:", m.group(1)[:200])

for m in re.finditer(r'(\.ytp-chrome-bottom[^{}]*\{[^{}]*\})', js):
    print("Chrome bottom CSS:", m.group(1)[:200])
