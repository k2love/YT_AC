import zipfile

with zipfile.ZipFile('YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk', 'r') as z:
    for name in z.namelist():
        if 'assets/' in name:
            info = z.getinfo(name)
            print(f'{name} -> size: {info.file_size}')
