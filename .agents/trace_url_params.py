import zipfile
import os
import re

base_dir = r"E:\AI_Projects\YouTube for Android TV\extracted"
main_apk = os.path.join(base_dir, "com.google.android.youtube.tv.apk")

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

print(f"Scanning classes2.dex ({len(dex2)/(1024*1024):.2f} MB)...")

# 1. 'cobalt.APP_URL' 주변의 문자열 패턴 추출
pos = 0
found_positions = []
while True:
    pos = dex2.find(b'cobalt.APP_URL', pos)
    if pos == -1:
        break
    found_positions.append(pos)
    pos += 14

print(f"Found 'cobalt.APP_URL' at {len(found_positions)} locations")

for p in found_positions:
    start = max(0, p - 300)
    end = min(len(dex2), p + 500)
    chunk = dex2[start:end]
    # ASCII 문자열들만 필터링해서 출력
    printable = re.findall(rb'[\x20-\x7E]{3,}', chunk)
    print("\n--- Context near cobalt.APP_URL ---")
    for s in printable:
        print(s.decode('latin1', errors='ignore'))

# 2. 'https://www.youtube.com/tv' 주변의 쿼리 파라미터나 URL 포맷팅 로직
pos2 = 0
found_urls = []
while True:
    pos2 = dex2.find(b'https://www.youtube.com/tv', pos2)
    if pos2 == -1:
        break
    found_urls.append(pos2)
    pos2 += 26

print(f"\nFound 'https://www.youtube.com/tv' at {len(found_urls)} locations")
for p in found_urls:
    start = max(0, p - 300)
    end = min(len(dex2), p + 600)
    chunk = dex2[start:end]
    printable = re.findall(rb'[\x20-\x7E]{3,}', chunk)
    print("\n--- Context near youtube.com/tv ---")
    for s in printable:
        print(s.decode('latin1', errors='ignore'))
