import re

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

with open(so_path, 'rb') as f:
    data = f.read()

target = b'h5vcc_system_impl_android'
pos = 0
found = []
while True:
    pos = data.find(target, pos)
    if pos == -1:
        break
    found.append(pos)
    pos += len(target)

print(f"Found '{target.decode()}' at {len(found)} locations:")
for offset in found:
    print(f"\n--- Location at offset 0x{offset:X} ---")
    start = max(0, offset - 300)
    end = min(len(data), offset + 1000)
    chunk = data[start:end]
    # null 바이트로 분리된 문자열 목록 출력
    strings = [s.decode('latin1', errors='ignore') for s in chunk.split(b'\x00') if len(s.strip()) > 1]
    for s in strings:
        print("  ", s)
