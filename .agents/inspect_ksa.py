with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('Ksa=function()')
if idx != -1:
    start = idx
    end = min(len(text), idx + 2000)
    print(text[start:end])
