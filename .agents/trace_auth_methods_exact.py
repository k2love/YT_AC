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

string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
proto_ids_size, proto_ids_off = struct.unpack('<II', dex2[0x48:0x50])
field_ids_size, field_ids_off = struct.unpack('<II', dex2[0x50:0x58])
method_ids_size, method_ids_off = struct.unpack('<II', dex2[0x58:0x60])
class_defs_size, class_defs_off = struct.unpack('<II', dex2[0x60:0x68])

def get_string(idx):
    if idx < 0 or idx >= string_ids_size:
        return f"<invalid str {idx}>"
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    if type_idx < 0 or type_idx >= type_ids_size:
        return f"<invalid type {type_idx}>"
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

def get_method_name(method_idx):
    if method_idx < 0 or method_idx >= method_ids_size:
        return f"<invalid method {method_idx}>", ""
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex2[method_ids_off + method_idx*8 : method_ids_off + (method_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

target_ids = [3513, 25652, 25653, 34556, 38054, 38258]

for tid in target_ids:
    s_val = get_string(tid)
    idx_bytes = struct.pack('<H', tid)
    pos = 0
    matches = []
    while True:
        pos = dex2.find(idx_bytes, pos)
        if pos == -1:
            break
        if pos >= 2 and dex2[pos-2] in (0x1A, 0x1B):
            matches.append(pos-2)
        pos += 2
    
    print(f"\nTarget [{tid}]: \"{s_val}\" (found {len(matches)} bytecode refs)")
    for m in matches:
        found = False
        for i in range(class_defs_size):
            cd_off = class_defs_off + i * 32
            class_idx, _, _, _, _, _, class_data_off, _ = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
            if class_data_off == 0:
                continue
            cur = class_data_off
            s_f, cur = read_uleb128(dex2, cur)
            i_f, cur = read_uleb128(dex2, cur)
            d_m, cur = read_uleb128(dex2, cur)
            v_m, cur = read_uleb128(dex2, cur)
            for _ in range(s_f + i_f):
                _, cur = read_uleb128(dex2, cur)
                _, cur = read_uleb128(dex2, cur)
            m_idx = 0
            for _ in range(d_m):
                diff, cur = read_uleb128(dex2, cur)
                m_idx += diff
                _, cur = read_uleb128(dex2, cur)
                code_off, cur = read_uleb128(dex2, cur)
                if code_off > 0:
                    _, _, _, _, _, insns_sz = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
                    if code_off + 16 <= m < code_off + 16 + insns_sz*2:
                        cn, mn = get_method_name(m_idx)
                        print(f"  -> Direct: {cn}->{mn}() at 0x{code_off:X} (in {get_type_name(class_idx)})")
                        found = True
            m_idx = 0
            for _ in range(v_m):
                diff, cur = read_uleb128(dex2, cur)
                m_idx += diff
                _, cur = read_uleb128(dex2, cur)
                code_off, cur = read_uleb128(dex2, cur)
                if code_off > 0:
                    _, _, _, _, _, insns_sz = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
                    if code_off + 16 <= m < code_off + 16 + insns_sz*2:
                        cn, mn = get_method_name(m_idx)
                        print(f"  -> Virtual: {cn}->{mn}() at 0x{code_off:X} (in {get_type_name(class_idx)})")
                        found = True
