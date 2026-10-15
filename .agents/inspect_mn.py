with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('_.On=function(')
if idx != -1:
    start = max(0, idx - 800)
    end = min(len(text), idx)
    print(text[start:end])
