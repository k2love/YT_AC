import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.youtube.com/s/player/0229cd64/tv-player-ias.vflset/tv-player-ias.js"
ua = "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"

js = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua})).read().decode('utf-8', errors='ignore')

target1 = "if(!N||!N.adPlacements&&!N.adSlots)return!1;"
target2 = "var n=this.playerResponse.playerAds;"
target3 = '"ad-showing"'

print("Length of tv-player-ias.js:", len(js))
print("target1 ('if(!N||!N.adPlacements&&!N.adSlots)return!1;'):", target1 in js)
print("target2 ('var n=this.playerResponse.playerAds;'):", target2 in js)
print("target3 ('\"ad-showing\"'):", target3 in js)
