with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'INTERACTION_KEY_ESCAPE', text)]
print(f"INTERACTION_KEY_ESCAPE matches: {len(matches)}")
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 200)
    print("--- MATCH ---")
    print(text[start:end])
