import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    # search for platformService or CobaltService
    targets = [b"platformService", b"PlatformService", b"h5vcc", b"registerCobaltService", b"sendToClient", b"receiveFromClient"]
    for t in targets:
        pos = 0
        count = 0
        print(f"\n--- Target: {t.decode()} ---")
        while count < 10:
            pos = mm.find(t, pos)
            if pos == -1:
                break
            start = max(0, pos - 40)
            end = min(mm.size(), pos + len(t) + 40)
            snippet = mm[start:end].replace(b'\x00', b' ')
            print(f"  [0x{pos:X}]: {snippet}")
            pos += len(t)
            count += 1
