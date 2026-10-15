with open('.agents/cached_tv.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()
import re
m = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
css = m[1]
print('Length:', len(css))
for rule in css.split('}'):
    if '{' in rule:
        sel = rule.split('{')[0].strip()
        body = rule.split('{')[1].strip()
        print(f'{sel} => len {len(body)}: {body[:60]}')
