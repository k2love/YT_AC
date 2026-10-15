with open(".agents/kabuki.css", "r", encoding="utf-8", errors="ignore") as f:
    css = f.read()

import re

# Find all rules containing gradient
rules = css.split('}')
print("Total rules:", len(rules))

gradient_rules = []
for r in rules:
    if '{' in r and 'gradient' in r:
        sel, body = r.split('{', 1)
        gradient_rules.append((sel.strip(), body.strip()))

print(f"Rules with gradient: {len(gradient_rules)}")
for sel, body in gradient_rules:
    print(f"SEL: {sel}")
    bgs = [prop.strip() for prop in body.split(';') if 'gradient' in prop or 'background' in prop]
    print(f"  {bgs}\n")
