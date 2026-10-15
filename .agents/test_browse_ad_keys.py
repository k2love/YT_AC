import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Call browse API with Cobalt UA to see exact JSON keys
browse_url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
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
    "browseId": "default"
}

req = urllib.request.Request(
    browse_url,
    data=json.dumps(body).encode('utf-8'),
    headers={
        "User-Agent": ua,
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("Browse API call successful! Keys:", list(res.keys()))
        
        # Search for ad keys in browse response
        found_ad_keys = []
        def find_keys(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if "ad" in k.lower() or "promot" in k.lower() or "masthead" in k.lower():
                        found_ad_keys.append(f"{path}.{k}")
                    find_keys(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    find_keys(v, f"{path}[{i}]")
                    
        find_keys(res)
        print(f"Found {len(found_ad_keys)} ad-related keys in browse response:")
        for k in found_ad_keys[:20]:
            print(" ", k)
except Exception as e:
    print("Error calling browse API:", e)
