import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    targets = [b"masthead", b"ad_slot", b"adBreak", b"adPlacements", b"in_feed_ad", b"ytlr_"]
    for t in targets:
        matches = set()
        pos = 0
        count = 0
        while count < 5:
            pos = mm.find(t, pos)
            if pos == -1:
                break
            start = max(0, pos - 20)
            end = min(mm.size(), pos + len(t) + 30)
            snippet = mm[start:end].replace(b'\x00', b' ')
            print(f"Target '{t.decode()}': {snippet}")
            pos += len(t)
            count += 1
