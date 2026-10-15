import urllib.request

url = 'https://www.youtube.com/tv?launch=menu'
ua = 'Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36'
req = urllib.request.Request(url, headers={'User-Agent': ua})
html = urllib.request.urlopen(req).read()
with open('.agents/cached_tv.html', 'wb') as f:
    f.write(html)
print('Cached HTML size:', len(html))
