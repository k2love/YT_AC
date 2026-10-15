import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

kabuki_path = "/s/_/kabuki/_/js/k=kabuki.base_cr.en_US.ev36-na5l9E.es5.O/am=AAAAAKAkACgAACJAAwqCiQI/d=1/excm=main/rs=ANjRhVkzcIezpZtQNeWHJ3K5kfzj9g26Zw/m=base"
url = f"https://www.youtube.com{kabuki_path}"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
print("Fetching Kabuki base script...")
js = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
print(f"Kabuki script size: {len(js)} bytes")

# Search for ad break, skip, player ad, etc.
keywords = ['adBreak', 'get_midroll', 'pagead', 'ad_break', 'adPlacements', 'adSlots', 'playerAds', 'skip_button']
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), js, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")
    for idx in matches[:3]:
        snippet = js[max(0, idx - 60):min(len(js), idx + 100)]
        print(f"   [{kw}] ...{snippet}...")
