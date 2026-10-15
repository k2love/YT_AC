import zipfile
import re

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

print(f"Inspecting DEX files for MainActivity and Auth flows...")

with zipfile.ZipFile(main_apk, 'r') as z:
    for dex_name in ['classes.dex', 'classes2.dex', 'classes3.dex']:
        data = z.read(dex_name)
        print(f"\n--- Checking {dex_name} ({len(data)/(1024*1024):.2f} MB) ---")
        
        # 1. MainActivity 및 ShellActivity 관련 클래스 검색
        act_matches = set(re.findall(rb'Lcom/google/android/apps/youtube/tv/activity/[a-zA-Z0-9_$]+;', data))
        for a in sorted(act_matches):
            print("  Activity class:", a.decode('latin1'))

        # 2. GMS Auth / Token 관련 키워드 검색
        auth_keywords = [
            b'com.google.android.gms.auth',
            b'GoogleAuthUtil',
            b'AccountManager',
            b'oauth2:',
            b'weblogin:',
            b'SID',
            b'HSID',
            b'SSID',
            b'APISID',
            b'SAPISID'
        ]
        for kw in auth_keywords:
            c = data.count(kw)
            if c > 0:
                print(f"  Keyword '{kw.decode()}': {c} occurrences")
