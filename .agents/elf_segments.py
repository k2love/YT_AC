import struct

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

with open(so_path, 'rb') as f:
    header = f.read(52)
    e_phoff = struct.unpack('<I', header[28:32])[0]
    e_phentsize = struct.unpack('<H', header[42:44])[0]
    e_phnum = struct.unpack('<H', header[44:46])[0]
    print(f"Program Headers: offset=0x{e_phoff:X}, entries={e_phnum}")
    
    f.seek(e_phoff)
    pt_loads = []
    for i in range(e_phnum):
        ph = f.read(e_phentsize)
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack('<IIIIIIII', ph[:32])
        if p_type == 1: # PT_LOAD
            pt_loads.append((p_offset, p_filesz, p_vaddr))
            print(f"PT_LOAD {i}: file offset 0x{p_offset:X}..0x{p_offset+p_filesz:X} -> VA 0x{p_vaddr:X}..0x{p_vaddr+p_memsz:X}")

def file_offset_to_va(fo):
    for p_offset, p_filesz, p_vaddr in pt_loads:
        if p_offset <= fo < p_offset + p_filesz:
            return p_vaddr + (fo - p_offset)
    return None

ua_fo = 0x4CDD1D
ua_va = file_offset_to_va(ua_fo)
print(f"\nUser-Agent template: file offset 0x{ua_fo:X} -> VA 0x{ua_va:X}")

url_fo1 = 0x30B64B
url_fo2 = 0x72B7B4
print(f"URL 1: file offset 0x{url_fo1:X} -> VA 0x{file_offset_to_va(url_fo1):X}")
print(f"URL 2: file offset 0x{url_fo2:X} -> VA 0x{file_offset_to_va(url_fo2):X}")
