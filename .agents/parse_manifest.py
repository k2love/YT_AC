import zipfile
import os
import re

base_dir = r"E:\AI_Projects\YouTube for Android TV\extracted"
main_apk = os.path.join(base_dir, "com.google.android.youtube.tv.apk")

with zipfile.ZipFile(main_apk, 'r') as z:
    manifest_data = z.read("AndroidManifest.xml")

# UTF-16LE 문자열 추출
utf16_matches = re.findall(rb'(?:[\x20-\x7e]\x00){3,}', manifest_data)
decoded = [m.decode('utf-16le', errors='ignore') for m in utf16_matches]

print(f"Total extracted strings: {len(decoded)}")
print("\n--- Key Component Names ---")
components = [s for s in decoded if any(k in s.lower() for k in ['activity', 'service', 'receiver', 'youtube', 'cobalt', 'launcher'])]
for c in sorted(set(components)):
    print(c)
