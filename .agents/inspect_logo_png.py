import urllib.request
import re
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

m = re.search(r'url\((data:image/png;base64,[^)]+)\)', html)
if m:
    data_uri = m.group(1)
    b64_data = data_uri.split(',', 1)[1]
    raw_bytes = base64.b64decode(b64_data)
    with open('E:\\AI_Projects\\## REA (Reverse Engineering Anything)\\.agents\\splash_logo.png', 'wb') as f:
        f.write(raw_bytes)
    print("Saved splash_logo.png. Size:", len(raw_bytes))

    # Read PNG header to inspect color type
    # PNG signature: 8 bytes, then IHDR chunk: 4 bytes len, 4 bytes type, 13 bytes data
    # IHDR data: width (4), height (4), bit depth (1), color type (1)
    ihdr = raw_bytes[12:29]
    width = int.from_bytes(ihdr[4:8], 'big')
    height = int.from_bytes(ihdr[8:12], 'big')
    bit_depth = ihdr[12]
    color_type = ihdr[13]
    print(f"PNG Dimension: {width}x{height}, Bit depth: {bit_depth}, Color type: {color_type}")
    # Color type: 0 (grayscale), 2 (truecolor), 3 (indexed), 4 (grayscale+alpha), 6 (truecolor+alpha)
    color_types = {0: "Grayscale", 2: "RGB (No Alpha!)", 3: "Indexed/Palette", 4: "Grayscale+Alpha", 6: "RGBA (Alpha)"}
    print(f"Color format: {color_types.get(color_type, 'Unknown')}")
