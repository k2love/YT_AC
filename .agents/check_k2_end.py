with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re
m = re.search(r'function k2\(N,L\)\{.+?return new DA\(0,\s*v,!1,"o"\)\}', js, re.DOTALL)
if m:
    print("Found k2 regex! Length:", len(m.group(0)))
    print("Prefix:", m.group(0)[:80])
    print("Suffix:", repr(m.group(0)[-80:]))
