import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/tv?launch=menu"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

# Find CSS link tags
for m in re.finditer(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*href=[\'"]([^\'"]+)[\'"]', html):
    print("Stylesheet link:", m.group(1))

# Check all style tags inside HTML
for m in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
    css = m.group(1)
    print("Style tag length:", len(css))
    if 'loader' in css:
        print("Found loader in style tag")
