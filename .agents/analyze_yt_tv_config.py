import urllib.request
import re
import json

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for ytcfg.set
matches = re.findall(r"ytcfg\.set\(\s*({.*?})\s*\);", html, re.DOTALL)
print(f"Found {len(matches)} ytcfg.set matches")
for idx, m in enumerate(matches):
    try:
        data = json.loads(m)
        print(f"\n--- Match {idx} keys: {list(data.keys())} ---")
        if "EXPERIMENT_FLAGS" in data:
            ef = data["EXPERIMENT_FLAGS"]
            ad_flags = {k: v for k, v in ef.items() if "ad" in k.lower()}
            print(f"  Total experiment flags: {len(ef)}, Ad flags: {len(ad_flags)}")
            for k, v in list(ad_flags.items())[:15]:
                print(f"    {k} = {v}")
    except Exception as e:
        print(f"Match {idx} JSON parse error:", e)

# Also search for ad keywords in HTML
ad_words = ["masthead", "adSlot", "adPlacement", "promoted", "inFeedAd"]
for w in ad_words:
    count = html.count(w)
    print(f"Occurrence of '{w}': {count}")
