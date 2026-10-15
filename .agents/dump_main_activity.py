import zipfile
import struct

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

class_defs_size, class_defs_off = struct.unpack('<II', dex2[0x60:0x68])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
method_ids_size, method_ids_off = struct.unpack('<II', dex2[0x50:0x58])

def get_string(idx):
    if idx >= string_ids_size:
        return ""
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    if type_idx >= type_ids_size:
        return ""
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

def get_method_name(method_idx):
    if method_idx >= method_ids_size:
        return "", ""
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex2[method_ids_off + method_idx*8 : method_ids_off + (method_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

target_class = "Lcom/google/android/apps/youtube/tv/activity/MainActivity;"

for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, _, superclass_idx, _, _, _, class_data_off, _ = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    cname = get_type_name(class_idx)
    if cname == target_class:
        super_name = get_type_name(superclass_idx)
        print(f"Class: {cname}")
        print(f"SuperClass: {super_name}")
        
        if class_data_off > 0:
            cur = class_data_off
            s_f, cur = read_uleb128(dex2, cur)
            i_f, cur = read_uleb128(dex2, cur)
            d_m, cur = read_uleb128(dex2, cur)
            v_m, cur = read_uleb128(dex2, cur)
            print(f"Methods: direct={d_m}, virtual={v_m}")
            
            for _ in range(s_f + i_f):
                _, cur = read_uleb128(dex2, cur)
                _, cur = read_uleb128(dex2, cur)
                
            m_idx = 0
            for _ in range(d_m + v_m):
                diff, cur = read_uleb128(dex2, cur)
                m_idx += diff
                _, cur = read_uleb128(dex2, cur)
                code_off, cur = read_uleb128(dex2, cur)
                _, mname = get_method_name(m_idx)
                print(f"  -> Method: {mname}()")
