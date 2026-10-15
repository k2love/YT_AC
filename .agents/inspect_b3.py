with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re
m = re.search(r'CF\.prototype\.B3=function\(N\)\{', js)
if m:
    idx = m.start()
    print(js[idx:idx+1500])
