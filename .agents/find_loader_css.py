import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

req = urllib.request.Request(url, headers={"User-Agent": ua})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Extract all CSS inside <style>
for m in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
    css = m.group(1)
    for rule in re.finditer(r'([^{}]*\{[^{}]*\})', css):
        r = rule.group(1)
        if 'loader' in r or 'splash' in r or 'logo' in r:
            print("CSS RULE:", r.strip()[:300])
