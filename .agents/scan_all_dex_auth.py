import zipfile
import struct

main_apk = r'E:\AI_Projects\YouTube for Android TV\extracted\com.google.android.youtube.tv.apk'

with zipfile.ZipFile(main_apk, 'r') as z:
    dex_names = [f for f in z.namelist() if f.endswith('.dex')]
    print(f"DEX files in APK: {dex_names}")
    
    for dex_name in sorted(dex_names):
        dex = z.read(dex_name)
        string_ids_size, string_ids_off = struct.unpack('<II', dex[0x38:0x40])
        
        def get_string(idx):
            if idx < 0 or idx >= string_ids_size:
                return ""
            off = struct.unpack('<I', dex[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
            length_bytes = 1
            while dex[off + length_bytes - 1] & 0x80:
                length_bytes += 1
            s_start = off + length_bytes
            s_end = dex.find(b'\x00', s_start)
            return dex[s_start:s_end].decode('latin1', errors='ignore')

        found_in_dex = []
        for i in range(string_ids_size):
            s = get_string(i)
            for target in ["url_params", "weblogin:", "oauth2:", "SAPISID", "APISID", "HSID", "SSID", "SID", "PREF", "ACCOUNT_NAME", "auth_token", "AccountManager"]:
                if target == s or (target in ["weblogin:", "oauth2:"] and target in s):
                    found_in_dex.append((i, s))
                    break
        if found_in_dex:
            print(f"\n--- {dex_name} (strings: {string_ids_size}) ---")
            for idx, s in found_in_dex:
                print(f"  [{idx}]: {s}")
