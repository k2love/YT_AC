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
proto_ids_size, proto_ids_off = struct.unpack('<II', dex2[0x48:0x50])
field_ids_size, field_ids_off = struct.unpack('<II', dex2[0x50:0x58])
method_ids_size, method_ids_off = struct.unpack('<II', dex2[0x58:0x60])
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

def get_method_name(method_idx):
    if method_idx < 0 or method_idx >= method_ids_size:
        return "", ""
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex2[method_ids_off + method_idx*8 : method_ids_off + (method_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

# Find all callers of Lejx methods
target_cname = "Lejx;"
target_type_idx = None
for i in range(type_ids_size):
    if get_type_name(i) == target_cname:
        target_type_idx = i
        break

print(f"Lejx type idx: {target_type_idx}")

# find method_ids for Lejx
lejx_methods = set()
for i in range(method_ids_size):
    c_idx, p_idx, n_idx = struct.unpack('<HHI', dex2[method_ids_off + i*8 : method_ids_off + (i+1)*8])
    if c_idx == target_type_idx:
        lejx_methods.add(i)

print(f"Lejx methods: {len(lejx_methods)}")

# search callers
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
    for _ in range(d_m + v_m):
        diff, cur = read_uleb128(dex2, cur)
        m_idx += diff
        _, cur = read_uleb128(dex2, cur)
        code_off, cur = read_uleb128(dex2, cur)
        if code_off > 0:
            _, _, _, _, _, insns_sz = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
            insns = dex2[code_off+16 : code_off+16+insns_sz*2]
            pc = 0
            while pc < len(insns) - 3:
                op = insns[pc]
                if op in (0x6E, 0x6F, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78):
                    callee_idx = struct.unpack('<H', insns[pc+2:pc+4])[0]
                    if callee_idx in lejx_methods:
                        caller_c, caller_m = get_method_name(m_idx)
                        callee_c, callee_m = get_method_name(callee_idx)
                        print(f"Caller: {caller_c}->{caller_m}() calls {callee_c}->{callee_m}()")
                pc += 2
