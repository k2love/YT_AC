with open(".agents/kabuki.css", "r", encoding="utf-8", errors="ignore") as f:
    css = f.read()

import re

# Split by }
rules = css.split('}')
print(f"Total rules in kabuki.css: {len(rules)}")

matched_rules = []
for r in rules:
    if '{' in r:
        sel, body = r.split('{', 1)
        sel = sel.strip()
        body = body.strip()
        
        # Check if selector or body relates to controls / overlay / scrim / menu / panel / player
        if any(k in sel for k in ["transport", "scrim", "gradient", "player", "overlay", "control", "menu", "panel", "title"]):
            if "background" in body:
                matched_rules.append((sel, body))

print(f"Matched background rules: {len(matched_rules)}")
for sel, body in matched_rules[:30]:
    print(f"SEL: {sel}")
    # Extract only background parts
    bgs = [prop.strip() for prop in body.split(';') if 'background' in prop or 'box-shadow' in prop]
    print(f"  BGS: {'; '.join(bgs)}")
