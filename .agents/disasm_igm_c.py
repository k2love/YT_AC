import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex2 = z.read("classes2.dex")

string_ids_size, string_ids_off = struct.unpack('<II', dex2[0x38:0x40])
type_ids_size, type_ids_off = struct.unpack('<II', dex2[0x40:0x48])
method_ids_size, method_ids_off = struct.unpack('<II', dex2[0x50:0x58])
field_ids_size, field_ids_off = struct.unpack('<II', dex2[0x48:0x50])

def get_string(idx):
    if idx >= string_ids_size:
        return f"<string#{idx}>"
    off = struct.unpack('<I', dex2[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    length_bytes = 1
    while dex2[off + length_bytes - 1] & 0x80:
        length_bytes += 1
    s_start = off + length_bytes
    s_end = dex2.find(b'\x00', s_start)
    return dex2[s_start:s_end].decode('latin1', errors='ignore')

def get_type_name(type_idx):
    if type_idx >= type_ids_size:
        return f"<type#{type_idx}>"
    desc_idx = struct.unpack('<I', dex2[type_ids_off + type_idx*4 : type_ids_off + (type_idx+1)*4])[0]
    return get_string(desc_idx)

def get_method_name(method_idx):
    if method_idx >= method_ids_size:
        return f"<method#{method_idx}>"
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex2[method_ids_off + method_idx*8 : method_ids_off + (method_idx+1)*8])
    return f"{get_type_name(class_idx)}->{get_string(name_idx)}"

def get_field_name(field_idx):
    if field_idx >= field_ids_size:
        return f"<field#{field_idx}>"
    class_idx, type_idx, name_idx = struct.unpack('<HHI', dex2[field_ids_off + field_idx*8 : field_ids_off + (field_idx+1)*8])
    return f"{get_type_name(class_idx)}->{get_string(name_idx)}"

# 0x4CF0C0..0x4CF2E6 디스어셈블
start_pc = 0x4CF0C0
end_pc = 0x4CF2E6
code = dex2[start_pc:end_pc]

print(f"Disassembling Ligm.c() from 0x{start_pc:X} to 0x{end_pc:X} (Size: {len(code)} bytes)...")

ip = 0
while ip < len(code):
    cur_pc = start_pc + ip
    op = code[ip]
    
    # 주요 Dalvik Opcode 해석
    if op == 0x1A: # const-string vAA, string@BBBB
        reg = code[ip+1]
        str_idx = struct.unpack('<H', code[ip+2:ip+4])[0]
        s_val = get_string(str_idx).encode('ascii', errors='replace').decode()
        print(f"0x{cur_pc:X}: const-string v{reg}, \"{s_val}\"")
        ip += 4
    elif op == 0x1B: # const-string/jumbo vAA, string@BBBBBBBB
        reg = code[ip+1]
        str_idx = struct.unpack('<I', code[ip+2:ip+6])[0]
        s_val = get_string(str_idx).encode('ascii', errors='replace').decode()
        print(f"0x{cur_pc:X}: const-string/jumbo v{reg}, \"{s_val}\"")
        ip += 6
    elif op in [0x6E, 0x6F, 0x70, 0x71, 0x72]: # invoke-kind {vC, vD...}, meth@BBBB
        meth_idx = struct.unpack('<H', code[ip+2:ip+4])[0]
        m_name = get_method_name(meth_idx)
        print(f"0x{cur_pc:X}: invoke-kind {m_name}")
        ip += 6
    elif op in [0x74, 0x75, 0x76, 0x77, 0x78]: # invoke-kind/range
        meth_idx = struct.unpack('<H', code[ip+2:ip+4])[0]
        m_name = get_method_name(meth_idx)
        print(f"0x{cur_pc:X}: invoke-kind/range {m_name}")
        ip += 6
    elif op in [0x52, 0x53, 0x54, 0x55, 0x59, 0x5A, 0x5B]: # iget/sget
        f_idx = struct.unpack('<H', code[ip+2:ip+4])[0]
        print(f"0x{cur_pc:X}: sget/iget {get_field_name(f_idx)}")
        ip += 4
    elif op in [0x5B, 0x5C, 0x5D, 0x5E, 0x5F, 0x67, 0x68]: # iput/sput
        f_idx = struct.unpack('<H', code[ip+2:ip+4])[0]
        print(f"0x{cur_pc:X}: sput/iput {get_field_name(f_idx)}")
        ip += 4
    elif op in [0x00]: # nop
        ip += 2
    elif op in [0x0E, 0x0F, 0x10, 0x11]: # return
        print(f"0x{cur_pc:X}: return")
        ip += 2
    else:
        ip += 2
