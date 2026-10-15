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
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

def get_method_name(method_idx):
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex2[method_ids_off + method_idx*8 : method_ids_off + (method_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

target_off = 0x7A26D
print(f"Finding owner of code offset 0x{target_off:X} across {class_defs_size} classes...")

found = False
for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    if class_data_off == 0:
        continue
    
    cur = class_data_off
    static_fields_size, cur = read_uleb128(dex2, cur)
    instance_fields_size, cur = read_uleb128(dex2, cur)
    direct_methods_size, cur = read_uleb128(dex2, cur)
    virtual_methods_size, cur = read_uleb128(dex2, cur)
    
    # skip fields
    for _ in range(static_fields_size + instance_fields_size):
        _, cur = read_uleb128(dex2, cur)
        _, cur = read_uleb128(dex2, cur)
        
    method_idx = 0
    for _ in range(direct_methods_size + virtual_methods_size):
        diff, cur = read_uleb128(dex2, cur)
        method_idx += diff
        access, cur = read_uleb128(dex2, cur)
        code_off, cur = read_uleb128(dex2, cur)
        
        if code_off > 0:
            reg_sz, ins_sz, outs_sz, tries_sz, dbg_off, insns_sz = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
            insns_start = code_off + 16
            insns_end = insns_start + insns_sz * 2
            if insns_start <= target_off < insns_end:
                cname, mname = get_method_name(method_idx)
                print(f"\n🎉 FOUND EXACT METHOD!")
                print(f"  Class:  {cname}")
                print(f"  Method: {mname}")
                print(f"  Code range: 0x{insns_start:X}..0x{insns_end:X}")
                found = True
                break
    if found:
        break
