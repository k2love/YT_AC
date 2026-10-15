import zipfile
import re

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

pos = 0
while True:
    pos = dex2.find(b'cert_scope', pos)
    if pos == -1:
        break
    print(f"\n--- Found 'cert_scope' at offset 0x{pos:X} in classes2.dex ---")
    start = max(0, pos - 400)
    end = min(len(dex2), pos + 500)
    chunk = dex2[start:end]
    strings = [s.decode('latin1', errors='ignore') for s in re.findall(rb'[\x20-\x7E]{3,}', chunk)]
    for s in strings:
        print("  ", s)
    pos += 10
