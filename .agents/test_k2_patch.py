with open(".agents/tv-player-ias.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find("function k2(N,L){")
if idx != -1:
    print(js[idx:idx+1200])
