import mmap
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    pos = 0x555A5D
    start = max(0, pos - 200)
    end = min(mm.size(), pos + 500)
    chunk = mm[start:end]
    printable = "".join(chr(b) if 32 <= b < 127 else " " for b in chunk)
    print(printable)
