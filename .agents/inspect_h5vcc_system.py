import re

so_path = r'E:\AI_Projects\YouTube for Android TV\extracted\config_armeabi_v7a\lib\armeabi-v7a\libchrobalt.so'

print(f"Scanning {so_path} for H5vccSystem details...")
with open(so_path, 'rb') as f:
    data = f.read()

# 1. H5vccSystem 관련 메서드 및 프로퍼티 검색
# C++ / Mojom / JavaScript 바인딩 이름들
system_keywords = [
    b'H5vccSystem',
    b'h5vcc_system',
    b'chipset_model_number',
    b'model_name',
    b'brand',
    b'platform_version',
    b'system_version',
    b'device_type',
    b'device_id',
    b'certification_version',
    b'advertising_id',
    b'limit_ad_tracking'
]

print("\n--- Keyword Occurrences in libchrobalt.so ---")
for kw in system_keywords:
    count = data.count(kw)
    print(f"'{kw.decode()}': {count} occurrences")

# 2. h5vcc_system.mojom 인터페이스 내 필드 및 메서드 시그니처 추출
# mojom 인터페이스 문자열 주변 문맥 분석
pos = 0
found_snippets = []
while True:
    pos = data.find(b'h5vcc_system', pos)
    if pos == -1:
        break
    start = max(0, pos - 200)
    end = min(len(data), pos + 400)
    snippet = data[start:end]
    found_snippets.append(snippet)
    pos += 12

print(f"\nFound {len(found_snippets)} h5vcc_system references. Inspecting unique surrounding identifiers...")
extracted_identifiers = set()
for s in found_snippets:
    ids = re.findall(rb'[a-zA-Z_][a-zA-Z0-9_]{3,60}', s)
    for i in ids:
        extracted_identifiers.add(i.decode('latin1', errors='ignore'))

for ident in sorted(extracted_identifiers):
    if any(k.lower() in ident.lower() for k in ['system', 'device', 'model', 'brand', 'version', 'h5vcc', 'prop', 'get']):
        print("  ->", ident)
