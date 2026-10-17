import os
import shutil
import subprocess
import sys

def build_all():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 60)
    print("YouTube TV AC - Multi-Platform Master Build Pipeline")
    print("Platforms: Android TV (APK) | Samsung Tizen (WGT) | LG webOS (IPK)")
    print("=" * 60)

    # 1. Sync Polyfill
    src_polyfill = os.path.join(root_dir, "app", "src", "main", "assets", "h5vcc_polyfill.js")
    tizen_polyfill = os.path.join(root_dir, "platforms", "tizen", "js", "h5vcc_polyfill.js")
    webos_polyfill = os.path.join(root_dir, "platforms", "webos", "js", "h5vcc_polyfill.js")

    print("\n[Step 1] Syncing h5vcc_polyfill.js across all platforms...")
    shutil.copy2(src_polyfill, tizen_polyfill)
    shutil.copy2(src_polyfill, webos_polyfill)
    print("  + Synced to Tizen & webOS.")

    # 2. Build Tizen WGT
    print("\n[Step 2] Building Samsung Tizen Package (.wgt)...")
    tizen_script = os.path.join(root_dir, "platforms", "tizen", "build_tizen.py")
    res_tizen = subprocess.run([sys.executable, tizen_script], cwd=os.path.dirname(tizen_script))
    if res_tizen.returncode != 0:
        print("  [ERROR] Tizen build failed!")

    # 3. Build webOS IPK
    print("\n[Step 3] Building LG webOS Package (.ipk)...")
    webos_script = os.path.join(root_dir, "platforms", "webos", "build_webos.py")
    res_webos = subprocess.run([sys.executable, webos_script], cwd=os.path.dirname(webos_script))
    if res_webos.returncode != 0:
        print("  [ERROR] webOS build failed!")

    print("\n" + "=" * 60)
    print("Master Build Pipeline Completed!")
    print("Outputs:")
    print("  - Android APK : " + os.path.join(root_dir, "YT_TV_AC.apk"))
    print("  - Samsung WGT : " + os.path.join(root_dir, "platforms", "tizen", "dist", "YT_TV_AC_Tizen.wgt"))
    print("  - LG webOS IPK: " + os.path.join(root_dir, "platforms", "webos", "dist", "YT_TV_AC_webOS.ipk"))
    print("=" * 60)

if __name__ == "__main__":
    build_all()
