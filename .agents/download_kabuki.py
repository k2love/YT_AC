import urllib.request
import re
import sys

ua = 'Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36'
url = 'https://www.youtube.com/s/_/kabuki/_/js/k=kabuki.base_cr.en_US.ev36-na5l9E.es5.O/am=AAAAAKAkACgAAKJAAwqCiQI/d=1/excm=main/rs=ANjRhVkJNKB4VbWyTwdkduspN1kgySoFzA/m=base'
req = urllib.request.Request(url, headers={'User-Agent': ua})
data = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
with open('.agents/kabuki_base.js', 'w', encoding='utf-8') as f:
    f.write(data)
print('Saved kabuki_base.js, len:', len(data))
