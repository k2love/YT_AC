import urllib.request
import re

ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

# 1. tv-player.css
player_css_url = "https://www.youtube.com/s/player/0229cd64/tv-player.css"
print("Downloading tv-player.css...")
req = urllib.request.Request(player_css_url, headers={"User-Agent": ua})
player_css = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
with open(".agents/tv-player.css", "w", encoding="utf-8") as f:
    f.write(player_css)
print("tv-player.css size:", len(player_css))

# 2. kabuki main stylesheet
kabuki_ss_url = "https://www.youtube.com/s/_/kabuki/_/ss/k=kabuki.base_cr.ObiNAht7iSE.L.W.O/am=AAAAAKAkACgAAKJAAwqCiQI/d=1/rs=ANjRhVnQf-QPHT7zxthu0eoV7BbJ6EDC1A/m=main"
print("Downloading kabuki stylesheet...")
req = urllib.request.Request(kabuki_ss_url, headers={"User-Agent": ua})
kabuki_css = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
with open(".agents/kabuki.css", "w", encoding="utf-8") as f:
    f.write(kabuki_css)
print("kabuki.css size:", len(kabuki_css))

# Analyze both for background gradients, scrims, blacks
print("\n--- ANALYZING tv-player.css ---")
for r in re.findall(r'([^{}]+\{[^{}]+\})', player_css):
    sel = r.split('{')[0].strip()
    body = r.split('{')[1].split('}')[0].strip()
    if any(k in body for k in ["gradient", "background:", "background-color:"]):
        if any(c in sel for c in ["chrome", "gradient", "control", "title", "overlay", "scrim", "bottom", "top", "menu", "panel"]):
            print(f"{sel} => {body}")

print("\n--- ANALYZING kabuki.css ---")
for r in re.findall(r'([^{}]+\{[^{}]+\})', kabuki_css):
    sel = r.split('{')[0].strip()
    body = r.split('{')[1].split('}')[0].strip()
    if any(k in body for k in ["gradient", "rgba(0,0,0", "rgba(0, 0, 0", "rgba(24,24,24", "#0f0f0f", "#181818"]):
        if any(c in sel for c in ["overlay", "scrim", "gradient", "controls", "transport", "panel", "menu", "watch"]):
            print(f"{sel} => {body}")
