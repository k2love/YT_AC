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

# 'cobalt.APP_URL'을 참조하는 클래스와 메서드 찾기
target_str = "cobalt.APP_URL"
target_idx = None
for i in range(string_ids_size):
    if get_string(i) == target_str:
        target_idx = i
        break

print(f"'{target_str}' string_id = {target_idx}")

idx_bytes = struct.pack('<H', target_idx)
pos = 0
matches = []
while True:
    pos = dex2.find(idx_bytes, pos)
    if pos == -1:
        break
    if pos >= 2 and dex2[pos-2] == 0x1A:
        matches.append(pos-2)
    pos += 2

print(f"Found {len(matches)} instructions using '{target_str}'")

for m in matches:
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
                insns_start = code_off + 16
                insns_end = insns_start + insns_sz * 2
                if insns_start <= m < insns_end:
                    cname, mname = get_method_name(m_idx)
                    print(f"-> Used in: {cname}->{mname}() at 0x{code_off:X}")
                    
                    # 이 메서드 디스어셈블
                    insns = dex2[insns_start:insns_end]
                    ip = 0
                    while ip < len(insns):
                        op = insns[ip]
                        if op == 0x1A:
                            s_i = struct.unpack('<H', insns[ip+2:ip+4])[0]
                            print(f"     const-string: \"{get_string(s_i)}\"")
                            ip += 4
                        elif op in [0x6E, 0x6F, 0x70, 0x71, 0x72]:
                            m_i = struct.unpack('<H', insns[ip+2:ip+4])[0]
                            cn, mn = get_method_name(m_i)
                            print(f"     invoke: {cn}->{mn}()")
                            ip += 6
                        else:
                            ip += 2
