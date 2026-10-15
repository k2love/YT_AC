import zipfile
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

def read_uleb128(data, offset):
    result = 0
    shift = 0
    while True:
        b = data[offset]
        offset += 1
        result |= (b & 0x7f) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, offset

string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
class_defs_size, class_defs_off = struct.unpack('<II', dex2[0x60:0x68])

def get_string(idx):
    if idx < 0 or idx >= string_ids_size:
        return ""
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    if type_idx < 0 or type_idx >= type_ids_size:
        return ""
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

# Find all classes implementing CobaltService or CobaltService$Factory or having superclass CobaltService
for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, access_flags, superclass_idx, interfaces_off, _, _, class_data_off, _ = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    cname = get_type_name(class_idx)
    sname = get_type_name(superclass_idx)
    
    # check interfaces
    interfaces = []
    if interfaces_off != 0:
        sz = struct.unpack('<I', dex2[interfaces_off:interfaces_off+4])[0]
        for j in range(sz):
            t_idx = struct.unpack('<H', dex2[interfaces_off+4+j*2 : interfaces_off+6+j*2])[0]
            interfaces.append(get_type_name(t_idx))
            
    is_match = False
    if "CobaltService" in sname:
        is_match = True
    for itf in interfaces:
        if "CobaltService" in itf:
            is_match = True
            
    if is_match or "CobaltService" in cname:
        print(f"CobaltService-related: {cname} extends {sname} implements {interfaces}")
