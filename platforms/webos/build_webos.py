import os
import io
import time
import tarfile
import subprocess
import shutil

def create_ar_file(output_path, members):
    """
    Creates a standard Debian/ipk ar archive without requiring external 'ar' utility.
    members: list of tuples (name, bytes_data)
    """
    with open(output_path, 'wb') as f:
        # 1. Global ar magic header
        f.write(b"!<arch>\n")

        for name, data in members:
            # 2. File header (60 bytes)
            # File identifier: 16 bytes (slash-terminated or space-padded)
            name_padded = (name.ljust(16))[:16].encode('ascii')
            # Modification timestamp: 12 bytes
            mtime = str(int(time.time())).ljust(12).encode('ascii')
            # Owner ID: 6 bytes
            uid = b"0     "
            # Group ID: 6 bytes
            gid = b"0     "
            # File mode: 8 bytes (octal 100644)
            mode = b"100644  "
            # File size: 10 bytes
            size = str(len(data)).ljust(10).encode('ascii')
            # Header trailer: 2 bytes
            trailer = b"`\n"

            header = name_padded + mtime + uid + gid + mode + size + trailer
            assert len(header) == 60, f"Header size must be 60 bytes, got {len(header)}"

            f.write(header)
            f.write(data)

            # 2-byte alignment padding
            if len(data) % 2 != 0:
                f.write(b"\n")

def build_webos_ipk():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    output_ipk = os.path.join(dist_dir, "YT_TV_AC_webOS.ipk")

    print("[webOS Build] Packaging LG webOS Application (.ipk)...")

    # Check if official ares-package is available
    ares_pkg = shutil.which("ares-package")
    if ares_pkg:
        try:
            print("  -> Found official ares-package tool, building with webOS CLI...")
            res = subprocess.run([ares_pkg, current_dir, "-o", dist_dir], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[webOS Build SUCCESS] {res.stdout.strip()}")
                return output_ipk
        except Exception as e:
            print(f"  -> ares-package failed ({e}), falling back to internal pure-Python packager.")

    # Pure Python standard .ipk builder (ar archive format)
    # 1. debian-binary
    debian_binary = b"2.0\n"

    # 2. control.tar.gz
    control_content = (
        "Package: com.k2.youtubetv.webos\n"
        "Version: 1.0.4\n"
        "Section: misc\n"
        "Priority: optional\n"
        "Architecture: all\n"
        "Maintainer: k2love\n"
        "Description: YouTube TV AC - Ultra-Clean Zero-Ad 4K Client for LG webOS\n"
    ).encode('utf-8')

    control_tar_io = io.BytesIO()
    with tarfile.open(fileobj=control_tar_io, mode='w:gz') as tar:
        ti = tarfile.TarInfo(name="./control")
        ti.size = len(control_content)
        ti.mtime = int(time.time())
        ti.mode = 0o644
        tar.addfile(ti, io.BytesIO(control_content))
    control_tar_gz = control_tar_io.getvalue()

    # 3. data.tar.gz
    app_base = "./usr/palm/applications/com.k2.youtubetv.webos"
    data_tar_io = io.BytesIO()
    with tarfile.open(fileobj=data_tar_io, mode='w:gz') as tar:
        # Base directories
        for d in ["./usr", "./usr/palm", "./usr/palm/applications", app_base]:
            ti = tarfile.TarInfo(name=d)
            ti.type = tarfile.DIRTYPE
            ti.mtime = int(time.time())
            ti.mode = 0o755
            tar.addfile(ti)

        # Include app files
        include_files = ["appinfo.json", "index.html", "icon.png", "largeIcon.png"]
        for f in include_files:
            file_path = os.path.join(current_dir, f)
            if os.path.exists(file_path):
                arcname = f"{app_base}/{f}"
                tar.add(file_path, arcname=arcname)
                print(f"  + Added file: {f}")

        # Include js directory
        js_dir = os.path.join(current_dir, "js")
        if os.path.exists(js_dir):
            for root, _, files in os.walk(js_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, current_dir).replace("\\", "/")
                    arcname = f"{app_base}/{rel_path}"
                    tar.add(full_path, arcname=arcname)
                    print(f"  + Added file: {rel_path}")

    data_tar_gz = data_tar_io.getvalue()

    # Assemble .ipk as ar archive: debian-binary, control.tar.gz, data.tar.gz
    members = [
        ("debian-binary", debian_binary),
        ("control.tar.gz", control_tar_gz),
        ("data.tar.gz", data_tar_gz)
    ]
    create_ar_file(output_ipk, members)

    size_mb = os.path.getsize(output_ipk) / (1024 * 1024)
    print(f"\n[webOS Build SUCCESS] Package created: {output_ipk} ({size_mb:.2f} MB)")
    return output_ipk

if __name__ == "__main__":
    build_webos_ipk()
