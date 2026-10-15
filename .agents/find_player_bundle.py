import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

# Search for any JS URLs
for m in re.finditer(r'[\'"]([^\'"]+?\.js)[\'"]', html):
    s = m.group(1)
    if 'player' in s.lower() or 'tv' in s.lower() or 'base' in s.lower():
        print("Found JS:", s)

# Search for WEB_PLAYER_CONTEXT_CONFIGS in ytcfg
for m in re.finditer(r'WEB_PLAYER_CONTEXT_CONFIGS\s*:\s*(\{.+?\})', html):
    print("WEB_PLAYER_CONTEXT_CONFIGS:", m.group(1)[:300])

# Search for PLAYER_VARS in ytcfg
for m in re.finditer(r'PLAYER_VARS\s*:\s*(\{.+?\})', html):
    print("PLAYER_VARS:", m.group(1)[:300])
