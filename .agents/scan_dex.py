import zipfile
import re
import os

base_dir = r"E:\AI_Projects\YouTube for Android TV\extracted"
main_apk = os.path.join(base_dir, "com.google.android.youtube.tv.apk")

print(f"Inspecting {main_apk}...")
with zipfile.ZipFile(main_apk, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            print(f"\n--- Checking {name} (Size: {len(content)/(1024*1024):.2f} MB) ---")
            
            # 1. chrobalt 관련 검색
            for m in set(re.findall(rb'[a-zA-Z0-9_/]{4,60}chrobalt[a-zA-Z0-9_/]*', content, re.IGNORECASE)):
                print("Found chrobalt:", m.decode('latin1', errors='ignore'))

            # 2. Cobalt 관련 검색
            cobalt_matches = set(re.findall(rb'[a-zA-Z0-9_/]{4,60}Cobalt[a-zA-Z0-9_/]*', content))
            for m in list(cobalt_matches)[:10]:
                print("Found Cobalt:", m.decode('latin1', errors='ignore'))

            # 3. youtube.com/tv 검색
            if b'youtube.com/tv' in content:
                print("Found 'youtube.com/tv' in", name)
