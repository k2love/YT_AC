import os
import shutil
import zipfile
import subprocess

def build_tizen_wgt():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    output_wgt = os.path.join(dist_dir, "YT_TV_AC_Tizen.wgt")

    print("[Tizen Build] Packaging Samsung Tizen Web Application (.wgt)...")

    # Files to include
    include_files = ["config.xml", "index.html", "icon.png"]
    include_dirs = ["js"]

    with zipfile.ZipFile(output_wgt, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in include_files:
            file_path = os.path.join(current_dir, f)
            if os.path.exists(file_path):
                z.write(file_path, arcname=f)
                print(f"  + Added file: {f}")

        for d in include_dirs:
            dir_path = os.path.join(current_dir, d)
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, current_dir)
                        z.write(full_path, arcname=rel_path)
                        print(f"  + Added file: {rel_path}")

    size_mb = os.path.getsize(output_wgt) / (1024 * 1024)
    print(f"\n[Tizen Build SUCCESS] Package created: {output_wgt} ({size_mb:.2f} MB)")
    return output_wgt

if __name__ == "__main__":
    build_tizen_wgt()
