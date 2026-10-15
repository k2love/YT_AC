with open(r'E:\AI_Projects\## YouTube TV for Android Clone\.agents\kabuki_base.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('_.On=function(')
if idx != -1:
    start = max(0, idx - 100)
    end = min(len(text), idx + 800)
    print(text[start:end])
else:
    print("Not found _.On")
