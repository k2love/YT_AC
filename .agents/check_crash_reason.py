with open('YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
dollars = [m.start() for m in re.finditer(r'\$', js)]
print('Dollar count in h5vcc_polyfill.js:', len(dollars))
for idx in dollars[:10]:
    print('Context:', repr(js[max(0, idx-20):min(len(js), idx+30)]))

slashes = [m.start() for m in re.finditer(r'\\', js)]
print('Backslash count in h5vcc_polyfill.js:', len(slashes))
for idx in slashes[:10]:
    print('Backslash Context:', repr(js[max(0, idx-20):min(len(js), idx+30)]))
