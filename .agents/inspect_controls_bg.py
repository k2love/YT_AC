import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# 1. Loader CSS & Image
m = re.search(r'#loader\s*\{([^}]+)\}', html)
if m:
    print("=== LOADER CSS ===")
    print(m.group(1))

# Extract image from loader
img_m = re.search(r'url\((data:image/png;base64,[^)]+)\)', html)
if img_m:
    data_uri = img_m.group(1)
    print("Data URI length:", len(data_uri))
    # Check first few bytes if valid PNG
    import base64
    raw_b64 = data_uri.split(',', 1)[1]
    img_bytes = base64.b64decode(raw_b64)
    print("Image byte size:", len(img_bytes))

# Search bundle js or inline styles for video player controls or background
for style_tag in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
    css = style_tag.group(1)
    for rule in re.finditer(r'([^{}]+\{[^{}]+\})', css):
        r = rule.group(1).strip()
        if 'background' in r.lower() and any(k in r.lower() for k in ['player', 'control', 'gradient', 'overlay', 'movie_player', 'app-background', 'container']):
            print("CSS RULE:", r[:200])
