import re

with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'\bJsa\b', text)]
print(f"Jsa calls: {len(matches)}")
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 200)
    print("--- CALL ---")
    print(text[start:end])
