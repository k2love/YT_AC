import mmap
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

so_path = r"E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so"

with open(so_path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    # search for strings near H5vccPlatformService
    pattern = re.compile(rb"H5vccPlatformService[A-Za-z0-9_:]*")
    matches = set(pattern.findall(mm))
    for m in sorted(matches):
        print(f"Found symbol/string: {m.decode(errors='ignore')}")
