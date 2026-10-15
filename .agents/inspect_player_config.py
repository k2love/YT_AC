import urllib.request
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

m = re.search(r"ytcfg\.set\(\s*({.*?})\s*\);", html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    player_configs = data.get("WEB_PLAYER_CONTEXT_CONFIGS", {})
    print("WEB_PLAYER_CONTEXT_CONFIGS keys:", list(player_configs.keys()))
    for k, v in player_configs.items():
        print(f"\n--- Config for {k} ---")
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                print(f"  {sub_k}: {type(sub_v)}")
                if "ad" in sub_k.lower() or "flag" in sub_k.lower():
                    print(f"    -> {sub_k} = {sub_v}")
        else:
            print(" ", str(v)[:200])
