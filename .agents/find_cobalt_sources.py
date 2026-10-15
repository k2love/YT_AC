import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    pattern = re.compile(rb"[a-zA-Z0-9_\-\./]*cobalt[a-zA-Z0-9_\-\./]*\.(?:cc|h)")
    matches = set(pattern.findall(mm))
    for m in sorted(matches):
        print(f"Cobalt source: {m.decode(errors='ignore')}")
