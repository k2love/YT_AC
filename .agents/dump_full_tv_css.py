with open(".agents/cached_tv.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

import re

m = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
if len(m) > 1:
    css = m[1]
    # search for overlay, player, menu, control, gradient, scrim, title, text, background
    rules = re.findall(r'([^{}]+\{[^{}]+\})', css)
    print("Total rules in Style #1:", len(rules))
    for r in rules:
        sel = r.split('{')[0].strip()
        body = r.split('{')[1].split('}')[0].strip()
        if any(k in sel.lower() for k in ["player", "overlay", "control", "menu", "scrim", "gradient", "title", "transport", "panel"]):
            print(f"SELECTOR: {sel}  ===>  {body}")
