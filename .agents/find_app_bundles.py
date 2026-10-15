with open('.agents/cached_tv.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()
import re

scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', html)
print("Scripts with src:", scripts)

links = re.findall(r'<link[^>]*href=[\'"]([^\'"]+)[\'"]', html)
print("Links with href:", links)

# Search for css or js strings
urls = set(re.findall(r'[\'"](/s/[^\'"]+)[\'"]', html))
print(f"URLs starting with /s/: {len(urls)}")
for u in sorted(urls):
    print(" ", u)
