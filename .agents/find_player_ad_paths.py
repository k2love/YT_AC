import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

player_url = 'https://www.youtube.com/youtubei/v1/player?prettyPrint=false'
ua = 'Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36'

video_ids = ['kJQP7kiw5Fk', '9bZkp7q19f0', 'fJ9rUzIMcZQ']
for vid in video_ids:
    body = {
        'context': {'client': {'clientName': 'TVHTML5', 'clientVersion': '7.20240101.00.00', 'gl': 'KR', 'hl': 'ko'}},
        'videoId': vid
    }
    req = urllib.request.Request(player_url, data=json.dumps(body).encode('utf-8'), headers={'User-Agent': ua, 'Content-Type': 'application/json'})
    try:
        resp = urllib.request.urlopen(req)
        res = json.loads(resp.read().decode('utf-8'))
        print(f'=== Video {vid} ===')
        for k in res:
            if any(term in k.lower() for term in ['ad', 'break', 'slot', 'playback', 'tracking']):
                print(f' - Key: {k}')
        def find_ad_paths(obj, path=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if any(term in k.lower() for term in ['adbreak', 'adplacement', 'adslot', 'playerad', 'instream', 'heartbeat']):
                        print(f'   Ad Node: {path}.{k}')
                    find_ad_paths(v, f'{path}.{k}')
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    find_ad_paths(v, f'{path}[{i}]')
        find_ad_paths(res)
    except Exception as e:
        print('Error:', e)
