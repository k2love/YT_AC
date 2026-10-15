import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

code_target_off = 0x7A26D

# DEX 헤더 파싱
class_defs_size, class_defs_off = struct.unpack('<II', dex2[0x60:0x68])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])

def get_string(idx):
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    # ULEB128 길이 건너뛰기
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

# code_item 위치 역추적
# class_def 구조체 (32바이트):
# class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off
found_class = None
for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    if class_data_off == 0:
        continue
    # class_data_item은 ULEB128로 인코딩됨
    # 간단히 class_data_off 이후 범위가 code_target_off 근처인지 체크
    cname = get_type_name(class_idx)
    # class_data_off 주변 확인
    if abs(class_data_off - code_target_off) < 0x20000:
        pass

# 더 정확하게: code_target_off 앞쪽의 메서드 헤더(code_item) 찾기
# code_item은 16바이트 헤더: registers_size(2), ins_size(2), outs_size(2), tries_size(2), debug_info_off(4), insns_size(4)
# 그 뒤에 insns 시작!
# code_target_off는 insns 내부이므로, insns_size를 역추적
print(f"Scanning for code_item owning offset 0x{code_target_off:X}...")
pos = code_target_off & ~3 # 4바이트 정렬
while pos > code_target_off - 1000:
    # insns 시작 오프셋 = pos
    # 헤더 오프셋 = pos - 16
    hdr_off = pos - 16
    if hdr_off >= 0:
        reg_sz, ins_sz, outs_sz, tries_sz, dbg_off, insns_sz = struct.unpack('<HHHHII', dex2[hdr_off:hdr_off+16])
        if insns_sz * 2 >= (code_target_off - pos) > 0 and reg_sz < 64 and ins_sz < 32:
            print(f"Found candidate code_item at 0x{hdr_off:X}: insns_sz={insns_sz} (bytes: {insns_sz*2}), regs={reg_sz}")
            break
    pos -= 4

# classes2.dex 내에서 method_id 및 class 검색
# 0x7A26D 주변 클래스 이름 탐색
p = code_target_off
chunk = dex2[max(0, p - 3000): min(len(dex2), p + 3000)]
import re
all_classes = set(re.findall(rb'L[a-zA-Z0-9_/]{5,60};', chunk))
print(f"\nNearby classes ({len(all_classes)}):")
for c in sorted(all_classes):
    print("  ", c.decode('latin1'))
