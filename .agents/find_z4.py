with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'\.Z4\s*=\s*function', js)]
print(f"Found {len(matches)} .Z4 = function occurrences")
for idx in matches:
    print(js[idx:idx+400])
    print("-" * 50)
