with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'mU\s*=', js)]
print(f"Found {len(matches)} mU = occurrences")
for idx in matches:
    print(js[max(0, idx-50):idx+150])
