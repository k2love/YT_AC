with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

print("Original JS len:", len(js))

# Test B3 patch
b3Target = "CF.prototype.B3=function(N){"
b3Idx = js.find(b3Target)
assert b3Idx != -1, "B3 target not found"
b3EndTarget = 'return new DA(0,L,!1,"r")};'
b3EndIdx = js.find(b3EndTarget, b3Idx)
assert b3EndIdx != -1, "B3 end target not found"
origB3 = js[b3Idx:b3EndIdx + len(b3EndTarget)]
print("B3 target found, len:", len(origB3))
uncapB3 = "CF.prototype.B3=function(N){return new DA(0,4320,!1,\"r\");};"
js2 = js.replace(origB3, uncapB3)
assert len(js2) < len(js)
print("B3 patch SUCCESS!")

# Test k2 patch
k2Target = "function k2(N,L){"
k2Idx = js2.find(k2Target)
assert k2Idx != -1, "k2 target not found"
k2EndTarget = 'return new DA(0,v,!1,"o")}'
k2EndIdx = js2.find(k2EndTarget, k2Idx)
assert k2EndIdx != -1, "k2 end target not found"
origK2 = js2[k2Idx:k2EndIdx + len(k2EndTarget)]
print("k2 target found, len:", len(origK2))
uncapK2 = "function k2(N,L){return new DA(0,4320,!1,\"o\");}"
js3 = js2.replace(origK2, uncapK2)
assert len(js3) < len(js2)
print("k2 patch SUCCESS!")

# Test w$n patch
import re
assert re.search(r'var\s+g=ar\(N\.G\.experiments,"html5_default_quality_cap"\);', js3) is not None
js4 = re.sub(r'var\s+g=ar\(N\.G\.experiments,"html5_default_quality_cap"\);', 'var g=4320;', js3)
print("w$n patch SUCCESS! Final length:", len(js4))
