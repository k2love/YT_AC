with open(r'E:\AI_Projects\## REA (Reverse Engineering Anything)\.agents\splash_logo.png', 'rb') as f:
    data = f.read()

# Check for tRNS chunk (Transparency chunk for indexed PNG)
trns_idx = data.find(b'tRNS')
print("Has tRNS transparency chunk:", trns_idx != -1)
if trns_idx != -1:
    trns_len = int.from_bytes(data[trns_idx-4:trns_idx], 'big')
    print("tRNS chunk length:", trns_len)

# Check PLTE chunk
plte_idx = data.find(b'PLTE')
if plte_idx != -1:
    plte_len = int.from_bytes(data[plte_idx-4:plte_idx], 'big')
    num_colors = plte_len // 3
    print(f"PLTE colors: {num_colors}")
    palette = data[plte_idx+4:plte_idx+4+plte_len]
    print("First 5 colors (RGB):", [tuple(palette[i:i+3]) for i in range(0, min(15, len(palette)), 3)])
