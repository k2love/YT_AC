with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re

# Find CSS strings inside tv-player-ias.js
css_matches = re.findall(r'(\.[a-zA-Z0-9_-]+(?:\{[^{}]+\}))', js)
print("CSS rules inside player JS:", len(css_matches))
for r in css_matches[:20]:
    if any(k in r for k in ["gradient", "chrome", "controls", "scrim", "panel", "menu", "popup", "background"]):
        print("CSS RULE:", r[:200])

# Also search class names
classes = set(re.findall(r'ytp-[a-zA-Z0-9-]+', js))
print(f"Unique ytp- classes: {len(classes)}")
for c in sorted(classes):
    if any(k in c for k in ["chrome", "gradient", "control", "menu", "panel", "popup", "scrim", "bottom", "top", "overlay", "title", "bezel", "spinner"]):
        print("  Class:", c)
