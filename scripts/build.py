"""Package the firmware into a versioned, reproducible zip + sha256 file.

Usage: python scripts/build.py 1.0.42
"""
import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXED_TIME = (2022, 1, 1, 0, 0, 0)  # fixed timestamp => identical zip for identical source


def main(version):
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    zip_path = dist / f"firmware-{version}.zip"

    source = (ROOT / "firmware" / "meter.py").read_text()
    source = source.replace('VERSION = "dev"', f'VERSION = "{version}"')

    files = {"meter.py": source, "version.txt": version + "\n"}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name])

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (dist / f"firmware-{version}.sha256").write_text(f"{digest}  {zip_path.name}\n")
    print(f"Built {zip_path.name} sha256={digest}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: build.py <version>")
    main(sys.argv[1])
