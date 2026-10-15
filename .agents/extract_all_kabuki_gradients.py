with open(".agents/kabuki.css", "r", encoding="utf-8", errors="ignore") as f:
    css = f.read()

import re

rules = css.split('}')
matched_selectors = []

for r in rules:
    if '{' in r:
        sel, body = r.split('{', 1)
        sel = sel.strip()
        body = body.strip()
        
        # Check if body has gradient
        if 'gradient(' in body:
            matched_selectors.append((sel, body))

print(f"Total gradient selectors: {len(matched_selectors)}")
for sel, body in matched_selectors:
    print(f"SEL: {sel}")
