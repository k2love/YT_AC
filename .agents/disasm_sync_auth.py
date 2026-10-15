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

def get_field_name(field_idx):
    if field_idx < 0 or field_idx >= field_ids_size:
        return "", ""
    class_idx, type_idx, name_idx = struct.unpack('<HHI', dex2[field_ids_off + field_idx*8 : field_ids_off + (field_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

def disasm(code_off):
    registers_size, ins_size, outs_size, tries_size, debug_info_off, insns_size = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
    insns_bytes = dex2[code_off+16 : code_off+16+insns_size*2]
    pc = 0
    while pc < len(insns_bytes):
        raw_pc = pc // 2
        op = insns_bytes[pc]
        line = f"    {raw_pc:04x}: "
        if op == 0x1A:
            s_i = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            line += f"const-string \"{get_string(s_i)}\""
            pc += 4
        elif op in (0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58):
            fld_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cn, fn = get_field_name(fld_idx)
            line += f"iget/iput {cn}->{fn}"
            pc += 4
        elif op in (0x6E, 0x6F, 0x70, 0x71, 0x72):
            m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cn, mn = get_method_name(m_idx)
            line += f"invoke {cn}->{mn}()"
            pc += 6
        elif op in (0x74, 0x75, 0x76, 0x77, 0x78):
            m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cn, mn = get_method_name(m_idx)
            line += f"invoke/range {cn}->{mn}()"
            pc += 6
        elif op == 0x0C:
            line += f"move-result-object v{insns_bytes[pc+1]}"
            pc += 2
        elif op == 0x0A:
            line += f"move-result v{insns_bytes[pc+1]}"
            pc += 2
        else:
            pc += 2
            continue
        print(line)

# Search Lgey
for i in range(class_defs_size):
    cd_off = class_defs_off + i * 32
    class_idx, _, superclass_idx, _, _, _, class_data_off, _ = struct.unpack('<IIIIIIII', dex2[cd_off:cd_off+32])
    cname = get_type_name(class_idx)
    if cname == "Lgey;":
        print(f"Disassembling {cname}:")
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
            cn, mn = get_method_name(m_idx)
            if code_off > 0:
                print(f"\n  Method {cn}->{mn}() at 0x{code_off:X}:")
                disasm(code_off)
