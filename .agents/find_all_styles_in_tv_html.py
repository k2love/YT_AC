with open(".agents/cached_tv.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

import re

for i, m in enumerate(re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)):
    content = m.group(1)
    print(f"Style #{i}: length {len(content)}")
    if len(content) > 0 and len(content) < 500:
        print(content)
    elif len(content) >= 500:
        print(content[:300], "...")
