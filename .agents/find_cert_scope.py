so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

with open(so_path, 'rb') as f:
    data = f.read()

target = b'ro.vendor.youtube.cert_scope'
pos = data.find(target)
print(f"Found '{target.decode()}' at offset: 0x{pos:X}")

start = max(0, pos - 200)
end = min(len(data), pos + 400)
chunk = data[start:end]
strings = [s.decode('latin1', errors='ignore') for s in chunk.split(b'\x00') if len(s.strip()) > 1]
for s in strings:
    print("  ", s)
