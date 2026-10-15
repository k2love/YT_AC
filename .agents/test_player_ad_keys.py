import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

player_url = "https://www.youtube.com/youtubei/v1/player?prettyPrint=false"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

body = {
    "context": {
        "client": {
            "clientName": "TVHTML5",
            "clientVersion": "7.20240101.00.00",
            "gl": "KR",
            "hl": "ko"
        }
    },
    "videoId": "dQw4w9WgXcQ"
}

req = urllib.request.Request(
    player_url,
    data=json.dumps(body).encode('utf-8'),
    headers={
        "User-Agent": ua,
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Player API call successful! Keys:", list(res.keys()))
        ad_keys = [k for k in res.keys() if "ad" in k.lower()]
        print("Top-level ad keys:", ad_keys)
        if "adPlacements" in res:
            print(f"adPlacements count: {len(res['adPlacements'])}")
            print("adPlacement 0:", json.dumps(res['adPlacements'][0])[:300])
        if "adSlots" in res:
            print(f"adSlots count: {len(res['adSlots'])}")
        if "playerAds" in res:
            print("playerAds found!")
except Exception as e:
    print("Error calling player API:", e)
