import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
for idx, s in enumerate(styles):
    if len(s) > 1000:
        print(f"Style {idx} (len {len(s)}):")
        # Find all rules with background or opacity
        for r in re.finditer(r'([^{}]+\{[^{}]+\})', s):
            rule = r.group(1).strip()
            if any(term in rule for term in ['#loader', '#app-background', '#container', 'transport', 'controls', 'overlay', 'movie_player', 'player']):
                print(" ->", rule[:120])
