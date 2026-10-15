with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

import re

# Test replacement 1: CF.prototype.B3
b3_regex = r'CF\.prototype\.B3=function\(N\)\{[^}]+qualityOrdinal[^}]+return new DA\(0,L,!1,"r"\)\};'
m = re.search(r'CF\.prototype\.B3=function\(N\)\{.+?return new DA\(0,L,!1,"r"\)\};', js)
if m:
    print("Found B3 target! Length:", len(m.group(0)))
    print("Snippet:", m.group(0)[:150], "...", m.group(0)[-100:])
else:
    print("B3 regex not matched directly, testing exact string")
    idx = js.find("CF.prototype.B3=function(N){")
    if idx != -1:
        end_idx = js.find('return new DA(0,L,!1,"r")};', idx)
        if end_idx != -1:
            full_b3 = js[idx:end_idx + len('return new DA(0,L,!1,"r")};')]
            print("Found via find! Length:", len(full_b3))
            print("Prefix:", full_b3[:100])
            print("Suffix:", full_b3[-100:])
