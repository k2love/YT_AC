with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('d.addEventListener("keydown",f,{capture:!0})')
if idx != -1:
    start = max(0, idx - 600)
    end = min(len(text), idx + 1000)
    print(text[start:end])
