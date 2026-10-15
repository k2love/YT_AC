import urllib.request
import re

url = 'https://www.youtube.com/tv?launch=menu'
ua = 'Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36'
req = urllib.request.Request(url, headers={'User-Agent': ua})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

m = re.search(r'#loader\s*\{[^}]+\}', html)
if m:
    print('Found #loader block (len):', len(m.group(0)))
    print('Block snippet:', m.group(0)[:120], '...', m.group(0)[-40:])
else:
    print('Not found')
