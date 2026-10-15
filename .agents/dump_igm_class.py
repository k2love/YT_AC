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
field_ids_size, field_ids_off = struct.unpack('<II', dex2[0x48:0x50])

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

for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, _, superclass_idx, _, _, _, class_data_off, _ = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    cname = get_type_name(class_idx)
    if cname == 'Ligm;':
        print(f"Class: {cname}, Super: {get_type_name(superclass_idx)}")
        cur = class_data_off
        s_f, cur = read_uleb128(dex2, cur)
        i_f, cur = read_uleb128(dex2, cur)
        d_m, cur = read_uleb128(dex2, cur)
        v_m, cur = read_uleb128(dex2, cur)
        
        # fields 건너뛰기
        for _ in range(s_f + i_f):
            _, cur = read_uleb128(dex2, cur)
            _, cur = read_uleb128(dex2, cur)
            
        m_idx = 0
        for _ in range(d_m + v_m):
            diff, cur = read_uleb128(dex2, cur)
            m_idx += diff
            access, cur = read_uleb128(dex2, cur)
            code_off, cur = read_uleb128(dex2, cur)
            _, proto_i, name_i = struct.unpack('<HHI', dex2[method_ids_off + m_idx*8 : method_ids_off + (m_idx+1)*8])
            mname = get_string(name_i)
            print(f"\nMethod: {mname}() [code_off=0x{code_off:X}]")
            
            if code_off > 0:
                _, _, _, _, _, insns_sz = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
                insns = dex2[code_off+16 : code_off+16+insns_sz*2]
                used_strings = set()
                ip = 0
                while ip < len(insns) - 1:
                    opcode = insns[ip]
                    if opcode == 0x1A: # const-string
                        str_idx = struct.unpack('<H', insns[ip+2:ip+4])[0]
                        used_strings.add(get_string(str_idx))
                        ip += 4
                    elif opcode == 0x1B: # const-string/jumbo
                        str_idx = struct.unpack('<I', insns[ip+2:ip+6])[0]
                        used_strings.add(get_string(str_idx))
                        ip += 6
                    else:
                        ip += 2
                for s in sorted(used_strings):
                    clean = s.encode('ascii', errors='replace').decode()
                    if len(clean.strip()) > 1:
                        print(f"    -> string: \"{clean}\"")
