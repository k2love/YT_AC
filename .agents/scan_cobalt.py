import re
import os

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

print(f"Reading {so_path}...")
with open(so_path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data) / (1024*1024):.2f} MB")

# 1. YouTube / Google / TV 관련 URL 검색
urls = set(re.findall(rb'https?://[a-zA-Z0-9_\-\./:\?#&=%]+', data))
yt_urls = [u.decode('latin1', errors='ignore') for u in urls if any(k in u for k in [b'youtube.com', b'googlevideo.com', b'googleapis.com', b'cobalt'])]
print(f"\n--- Found {len(yt_urls)} YouTube/Google URLs (Sample Top 30) ---")
for u in sorted(yt_urls)[:30]:
    print(u)

# 2. User-Agent 검색
ua_matches = set(re.findall(rb'Mozilla/5\.0[^\x00\r\n]{10,120}', data))
print(f"\n--- Found User-Agents ({len(ua_matches)}) ---")
for ua in sorted(ua_matches)[:10]:
    print(ua.decode('latin1', errors='ignore'))

# 3. 주요 키워드 출현 횟수
keywords = [b'cobalt', b'starboard', b'device_id', b'certification', b'innertube', b'user_agent', b'youtube.com/tv', b'dial', b'lounge']
print("\n--- Keyword Frequencies ---")
for kw in keywords:
    print(f"'{kw.decode()}': {data.count(kw)}")
