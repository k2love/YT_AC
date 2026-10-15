import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

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

def get_field_name(field_idx):
    if field_idx < 0 or field_idx >= field_ids_size:
        return f"<invalid field {field_idx}>", ""
    class_idx, type_idx, name_idx = struct.unpack('<HHI', dex2[field_ids_off + field_idx*8 : field_ids_off + (field_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

def disasm_method(name, code_off):
    registers_size, ins_size, outs_size, tries_size, debug_info_off, insns_size = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
    print(f"\n==================== {name} at 0x{code_off:X} ====================")
    print(f"regs={registers_size}, ins={ins_size}, outs={outs_size}, insns_size={insns_size}")
    insns_bytes = dex2[code_off+16 : code_off+16+insns_size*2]
    
    pc = 0
    while pc < len(insns_bytes):
        raw_pc = pc // 2
        op = insns_bytes[pc]
        line = f"  {raw_pc:04x}: (0x{op:02x}) "
        
        if op == 0x00:
            line += "nop"
            pc += 2
        elif op == 0x1A:
            reg = insns_bytes[pc+1]
            str_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            line += f"const-string v{reg}, \"{get_string(str_idx)}\""
            pc += 4
        elif op == 0x1B:
            reg = insns_bytes[pc+1]
            str_idx = struct.unpack('<I', insns_bytes[pc+2:pc+6])[0]
            line += f"const-string/jumbo v{reg}, \"{get_string(str_idx)}\""
            pc += 6
        elif op in (0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58):
            reg = insns_bytes[pc+1] & 0x0F
            obj = (insns_bytes[pc+1] >> 4) & 0x0F
            fld_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cname, fname = get_field_name(fld_idx)
            line += f"iget/iput v{reg}, v{obj}, {cname}->{fname}"
            pc += 4
        elif op in (0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66):
            reg = insns_bytes[pc+1]
            fld_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cname, fname = get_field_name(fld_idx)
            line += f"sget/sput v{reg}, {cname}->{fname}"
            pc += 4
        elif op in (0x6E, 0x6F, 0x70, 0x71, 0x72):
            count = (insns_bytes[pc+1] >> 4) & 0x0F
            m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cname, mname = get_method_name(m_idx)
            line += f"invoke (op {op:02x}): {cname}->{mname}()"
            pc += 6
        elif op in (0x74, 0x75, 0x76, 0x77, 0x78):
            count = insns_bytes[pc+1]
            m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            cname, mname = get_method_name(m_idx)
            line += f"invoke/range ({count} args): {cname}->{mname}()"
            pc += 6
        elif op == 0x0C:
            line += f"move-result-object v{insns_bytes[pc+1]}"
            pc += 2
        elif op == 0x0A:
            line += f"move-result v{insns_bytes[pc+1]}"
            pc += 2
        elif op == 0x12:
            reg = insns_bytes[pc+1] & 0x0F
            val = (insns_bytes[pc+1] >> 4) & 0x0F
            line += f"const/4 v{reg}, #{val}"
            pc += 2
        elif op in (0x28, 0x29, 0x2A):
            line += "goto ..."
            pc += 2 if op == 0x28 else (4 if op == 0x29 else 6)
        elif op in (0x38, 0x39):
            reg = insns_bytes[pc+1]
            target = struct.unpack('<h', insns_bytes[pc+2:pc+4])[0]
            line += f"if v{reg} goto {raw_pc + target:04x}"
            pc += 4
        elif op in (0x32, 0x33, 0x34, 0x35, 0x36, 0x37):
            regA = insns_bytes[pc+1] & 0x0F
            regB = (insns_bytes[pc+1] >> 4) & 0x0F
            target = struct.unpack('<h', insns_bytes[pc+2:pc+4])[0]
            line += f"if-cmp v{regA}, v{regB} goto {raw_pc + target:04x}"
            pc += 4
        elif op in (0x0E, 0x0F, 0x10, 0x11):
            line += "return"
            pc += 2
        elif op == 0x22:
            reg = insns_bytes[pc+1]
            type_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            line += f"new-instance v{reg}, {get_type_name(type_idx)}"
            pc += 4
        elif op == 0x1C:
            reg = insns_bytes[pc+1]
            type_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
            line += f"const-class v{reg}, {get_type_name(type_idx)}"
            pc += 4
        else:
            line += f"op 0x{op:02x}"
            pc += 2
        print(line)

disasm_method("Lejx;->e()", 0x33B464)
disasm_method("Lell;-><init>()", 0x340D04)
disasm_method("Lghl;->g()", 0x3E7374)
