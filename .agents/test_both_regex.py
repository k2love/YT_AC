with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re

# B3
m_b3 = re.search(r'CF\.prototype\.B3=function\(N\)\{.+?return new DA\(0,L,!1,"r"\)\};', js, re.DOTALL)
assert m_b3 is not None
print("m_b3 matched len:", len(m_b3.group(0)))

# k2
m_k2 = re.search(r'function k2\(N,L\)\{.+?return new DA\(0,\s*v,!1,"o"\)\}', js, re.DOTALL)
assert m_k2 is not None
print("m_k2 matched len:", len(m_k2.group(0)))

# w$n
m_wn = re.search(r'var\s+g=ar\(N\.G\.experiments,"html5_default_quality_cap"\);', js)
assert m_wn is not None
print("m_wn matched len:", len(m_wn.group(0)))

print("ALL 3 MATCHED PERFECTLY!")
