import struct

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

with open(so_path, 'rb') as f:
    data = f.read()

target = b'https://www.youtube.com/tv'
pos = 0
found = []
while True:
    pos = data.find(target, pos)
    if pos == -1:
        break
    found.append(pos)
    pos += len(target)

print(f"Target '{target.decode()}' found at offsets:")
for offset in found:
    print(f"File Offset: 0x{offset:X}")
    
    # 4바이트 정렬된 가상 주소 포인터 검색 (ARM Little Endian)
    # ELF 헤더의 기본 로드 주소(Image Base) 고려 (보통 0x0)
    ptr_32 = struct.pack('<I', offset)
    ptr_pos = 0
    ref_count = 0
    while True:
        ptr_pos = data.find(ptr_32, ptr_pos)
        if ptr_pos == -1:
            break
        print(f"  -> Referenced by pointer at file offset: 0x{ptr_pos:X}")
        ref_count += 1
        ptr_pos += 4
    if ref_count == 0:
        print("  (No direct 32-bit absolute pointer found - might be PC-relative or ADRP/LDR)")

# User-Agent 문자열 위치도 확인
ua_target = b'Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) %s Safari/537.36'
ua_pos = data.find(ua_target)
if ua_pos != -1:
    print(f"\nUser-Agent template found at file offset: 0x{ua_pos:X}")
    # 주변 문자열 출력
    start = max(0, ua_pos - 100)
    end = min(len(data), ua_pos + 200)
    print("Surrounding strings:")
    for s in data[start:end].split(b'\x00'):
        if s.strip():
            print("  ", s.decode('latin1', errors='ignore'))
