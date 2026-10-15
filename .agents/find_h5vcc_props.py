import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    # search for "h5vcc" in idl or string tables
    # Find all occurrences of b"h5vcc."
    matches = set()
    pos = 0
    while True:
        pos = mm.find(b"h5vcc.", pos)
        if pos == -1:
            break
        snippet = mm[pos:pos+30]
        end = snippet.find(b'\x00')
        if end != -1:
            snippet = snippet[:end]
        matches.add(snippet)
        pos += 6
        
    for m in sorted(matches):
        print(f"h5vcc prop: {m.decode(errors='ignore')}")
