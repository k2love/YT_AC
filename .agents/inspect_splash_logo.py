import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

for m in re.finditer(r'([^{}]*(?:splash|loader)[^{}]*\{[^{}]*\})', html, re.I):
    rule = m.group(1).strip()
    if 'loader' in rule or 'splash' in rule:
        print(rule)
        print("-" * 40)
