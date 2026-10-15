with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'var mU\s*=', js)]
print(f"Found {len(matches)} var mU = occurrences")
for idx in matches:
    print(js[idx:idx+200])
