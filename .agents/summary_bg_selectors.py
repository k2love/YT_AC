with open(".agents/youtube_tv_inline_css.css", "r", encoding="utf-8") as f:
    css = f.read()

import re
rules = re.findall(r'([^{}]+\{[^{}]+\})', css)
for r in rules:
    sel = r.split('{')[0].strip()
    body = r.split('{')[1].split('}')[0].strip()
    if "background" in body:
        print(f"{sel} => {body}")
