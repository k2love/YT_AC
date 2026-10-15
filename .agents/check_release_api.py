import urllib.request
import json

url = 'https://api.github.com/repos/k2love/YT_AC/releases/latest'
req = urllib.request.Request(url, headers={'User-Agent': 'YT_TV_AC-Test'})
try:
    res = urllib.request.urlopen(req)
    print('HTTP Code:', res.status)
    data = json.loads(res.read().decode('utf-8'))
    print('Release tag:', data.get('tag_name'))
    print('Release name:', data.get('name'))
    print('Assets:', len(data.get('assets', [])))
    for a in data.get('assets', []):
        print('  Asset:', a.get('name'), a.get('browser_download_url'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.reason)
    print('Body:', e.read().decode('utf-8', errors='ignore'))
except Exception as e:
    print('Error:', e)
