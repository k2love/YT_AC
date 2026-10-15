import re

with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

patterns = [
    r'.{0,40}keyCode\s*===?\s*27.{0,40}',
    r'.{0,40}keyCode\s*===?\s*8\b.{0,40}',
    r'.{0,40}keyCode\s*===?\s*461.{0,40}',
    r'.{0,40}keyCode\s*===?\s*10009.{0,40}',
    r'.{0,40}Escape.{0,40}',
    r'.{0,40}BrowserBack.{0,40}',
    r'.{0,40}GoBack.{0,40}',
    r'.{0,40}history\.back.{0,40}',
]

for p in patterns:
    m = re.findall(p, text)
    print(f"Pattern {p}: {len(m)} matches")
    for sample in m[:3]:
        print("  ", repr(sample.strip()))
