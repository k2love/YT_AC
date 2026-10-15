import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    pos = 0
    count = 0
    while count < 15:
        pos = mm.find(b"H5vccPlatformServiceManagerImpl::Open", pos)
        if pos == -1:
            break
        print(f"Match at 0x{pos:X}")
        # search backward and forward for strings
        start = max(0, pos - 200)
        end = min(mm.size(), pos + 400)
        chunk = mm[start:end]
        printable = "".join(chr(b) if 32 <= b < 127 else " " for b in chunk)
        print(printable)
        pos += 10
        count += 1
