import re

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

with open(so_path, 'rb') as f:
    data = f.read()

# 1. SbSystem* 함수 및 심볼 검색
matches = set(re.findall(rb'SbSystem[a-zA-Z0-9_]*', data))
print("--- Found SbSystem Functions ---")
for m in sorted(matches):
    print(m.decode('latin1'))

# 2. kSbSystemProperty* 상수 검색 (Starboard 시스템 프로퍼티 열거형)
prop_matches = set(re.findall(rb'kSbSystemProperty[a-zA-Z0-9_]*', data))
print("\n--- Found kSbSystemProperty Constants ---")
for p in sorted(prop_matches):
    print(p.decode('latin1'))

# 3. Android SystemProperties (getprop / ro.*) 검색
ro_matches = set(re.findall(rb'ro\.[a-zA-Z0-9_\.]+', data))
print("\n--- Found Android System Properties (ro.*) ---")
for r in sorted(ro_matches):
    print(r.decode('latin1'))
