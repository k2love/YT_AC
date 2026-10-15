import re

with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find("INTERACTION_KEY_ESCAPE")
if idx != -1:
    start = max(0, idx - 500)
    end = min(len(text), idx + 500)
    print(text[start:end])
else:
    print("Not found")
