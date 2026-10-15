import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

target_str = b"Failed to read system property ro.vendor.youtube.cert_scope"
str_pos = dex2.find(target_str)
print(f"String offset: 0x{str_pos:X}")

# DEX 헤더 파싱
string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
print(f"string_ids: count={string_ids_size}, off=0x{string_ids_off:X}")

# string_ids 테이블에서 target_str을 가리키는 string_id_index 검색
target_str_idx = None
for i in range(string_ids_size):
    str_data_off = struct.unpack('<I', dex2[string_ids_off + i*4 : string_ids_off + (i+1)*4])[0]
    # ULEB128 길이 바이트 건너뛰기
    data_start = str_data_off + 1
    if dex2[data_start:data_start+len(target_str)] == target_str:
        target_str_idx = i
        print(f"Found string_id index: {target_str_idx} (0x{target_str_idx:X})")
        break

if target_str_idx is not None:
    # bytecode에서 const-string (0x1A) 또는 const-string/jumbo (0x1B) 검색
    # const-string: 1A AA BBBB (BBBB is string_id index)
    # const-string/jumbo: 1B AA BBBBBBBB
    pattern1 = struct.pack('<BH', 0x1A, target_str_idx)
    pattern2 = struct.pack('<BI', 0x1B, target_str_idx)
    
    code_pos = dex2.find(pattern1)
    if code_pos != -1:
        print(f"const-string found at code offset: 0x{code_pos:X}")
    else:
        code_pos = dex2.find(pattern2)
        if code_pos != -1:
            print(f"const-string/jumbo found at code offset: 0x{code_pos:X}")
    
    if code_pos != -1:
        # 이 코드 주변에서 클래스/메서드 단서 탐색
        start = max(0, code_pos - 400)
        end = min(len(dex2), code_pos + 400)
        chunk = dex2[start:end]
        import re
        classes = re.findall(rb'L[a-zA-Z0-9_/]{4,60};', chunk)
        print("Associated Class Signatures:")
        for c in set(classes):
            print("  ", c.decode('latin1'))
