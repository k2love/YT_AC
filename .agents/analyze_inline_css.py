with open(".agents/youtube_tv_inline_css.css", "r", encoding="utf-8") as f:
    css = f.read()

import re

rules = re.findall(r'([^{}]+\{[^{}]+\})', css)
print("Total rules:", len(rules))

bg_rules = []
for r in rules:
    if "background" in r or "color" in r:
        bg_rules.append(r.strip())

print(f"Rules with background/color: {len(bg_rules)}")
for r in bg_rules:
    # Look for selectors
    sel = r.split('{')[0].strip()
    body = r.split('{')[1].split('}')[0].strip()
    if any(k in body for k in ["#", "rgb", "gradient", "black", "000"]):
        print(f"SELECTOR: {sel}")
        print(f"  BODY: {body}\n")
