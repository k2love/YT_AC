import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

class_defs_size, class_defs_off = struct.unpack('<II', dex2[0x60:0x68])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
method_ids_size, method_ids_off = struct.unpack('<II', dex2[0x50:0x58])
field_ids_size, field_ids_off = struct.unpack('<II', dex2[0x48:0x50]) # wait, field_ids is at 0x48? No, let's check field_ids offset in DEX

# DEX header offsets:
# 0x30: proto_ids_size, proto_ids_off
# 0x38: field_ids_size, field_ids_off
# 0x40: method_ids_size, method_ids_off
# Wait, let's verify header format:
# magic: 8
# checksum: 4
# signature: 20
# file_size: 4
# header_size: 4
# endian_tag: 4
# link_size: 4
# link_off: 4
# map_off: 4
# string_ids_size: 4 (0x38)
# string_ids_off: 4 (0x3c)
# type_ids_size: 4 (0x40)
# type_ids_off: 4 (0x44)
# proto_ids_size: 4 (0x48)
# proto_ids_off: 4 (0x4c)
# field_ids_size: 4 (0x50)
# field_ids_off: 4 (0x54)
# method_ids_size: 4 (0x58)
# method_ids_off: 4 (0x5c)
# class_defs_size: 4 (0x60)
# class_defs_off: 4 (0x64)

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

code_off = 0x4CE3E0
registers_size, ins_size, outs_size, tries_size, debug_info_off, insns_size = struct.unpack('<HHHHII', dex2[code_off:code_off+16])
print(f"Method at 0x{code_off:X}: registers={registers_size}, ins={ins_size}, outs={outs_size}, insns_size={insns_size}")

insns_bytes = dex2[code_off+16 : code_off+16+insns_size*2]

# Dalvik instruction format parsing
pc = 0
while pc < len(insns_bytes):
    raw_pc = pc // 2
    op = insns_bytes[pc]
    line = f"{raw_pc:04x}: (0x{op:02x}) "
    
    # Simple decoder for common instructions
    if op == 0x00: # nop
        line += "nop"
        pc += 2
    elif op == 0x1A: # const-string vAA, string@BBBB
        reg = insns_bytes[pc+1]
        str_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        line += f"const-string v{reg}, \"{get_string(str_idx)}\""
        pc += 4
    elif op == 0x1B: # const-string/jumbo vAA, string@BBBBBBBB
        reg = insns_bytes[pc+1]
        str_idx = struct.unpack('<I', insns_bytes[pc+2:pc+6])[0]
        line += f"const-string/jumbo v{reg}, \"{get_string(str_idx)}\""
        pc += 6
    elif op in (0x52, 0x53, 0x54, 0x55): # iget / iput
        reg = insns_bytes[pc+1] & 0x0F
        obj = (insns_bytes[pc+1] >> 4) & 0x0F
        fld_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        cname, fname = get_field_name(fld_idx)
        line += f"iget/iput v{reg}, v{obj}, {cname}->{fname}"
        pc += 4
    elif op in (0x60, 0x61, 0x62, 0x63): # sget / sput
        reg = insns_bytes[pc+1]
        fld_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        cname, fname = get_field_name(fld_idx)
        line += f"sget/sput v{reg}, {cname}->{fname}"
        pc += 4
    elif op in (0x6E, 0x6F, 0x70, 0x71, 0x72): # invoke-kind {vC, vD, ...}, meth@BBBB
        count = (insns_bytes[pc+1] >> 4) & 0x0F
        m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        cname, mname = get_method_name(m_idx)
        line += f"invoke (op {op:02x}, {count} args): {cname}->{mname}()"
        pc += 6
    elif op in (0x74, 0x75, 0x76, 0x77, 0x78): # invoke-kind/range {vCCCC .. vNNNN}, meth@BBBB
        count = insns_bytes[pc+1]
        m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        cname, mname = get_method_name(m_idx)
        line += f"invoke/range ({count} args): {cname}->{mname}()"
        pc += 6
    elif op == 0x0C: # move-result-object
        reg = insns_bytes[pc+1]
        line += f"move-result-object v{reg}"
        pc += 2
    elif op == 0x0A: # move-result
        reg = insns_bytes[pc+1]
        line += f"move-result v{reg}"
        pc += 2
    elif op == 0x12: # const/4
        reg = insns_bytes[pc+1] & 0x0F
        val = (insns_bytes[pc+1] >> 4) & 0x0F
        line += f"const/4 v{reg}, #{val}"
        pc += 2
    elif op in (0x28, 0x29, 0x2A): # goto
        line += f"goto ..."
        pc += 2 if op == 0x28 else (4 if op == 0x29 else 6)
    elif op in (0x38, 0x39): # if-eqz, if-nez
        reg = insns_bytes[pc+1]
        target = struct.unpack('<h', insns_bytes[pc+2:pc+4])[0]
        line += f"if v{reg} goto {raw_pc + target:04x}"
        pc += 4
    elif op in (0x0E, 0x0F, 0x10, 0x11): # return
        line += f"return"
        pc += 2
    elif op == 0x22: # new-instance
        reg = insns_bytes[pc+1]
        type_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        line += f"new-instance v{reg}, {get_type_name(type_idx)}"
        pc += 4
    elif op == 0x23: # new-array
        reg = insns_bytes[pc+1] & 0x0F
        type_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        line += f"new-array v{reg}, {get_type_name(type_idx)}"
        pc += 4
    elif op == 0x1C: # const-class
        reg = insns_bytes[pc+1]
        type_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
        line += f"const-class v{reg}, {get_type_name(type_idx)}"
        pc += 4
    elif op == 0x26: # fill-array-data
        line += f"fill-array-data"
        pc += 6
    else:
        line += f"instruction 0x{op:02x}"
        pc += 2
        
    print(line)
