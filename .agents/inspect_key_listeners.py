import re

with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'addEventListener\(["\']key', text)]
print(f"addEventListener key matches: {len(matches)}")
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 200)
    print("--- MATCH ---")
    print(text[start:end])
