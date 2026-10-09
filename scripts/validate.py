"""Validate a built firmware package. Exits non-zero on any failure.

Usage: python scripts/validate.py dist
"""
import hashlib
import sys
import zipfile
from pathlib import Path

MAX_SIZE_BYTES = 64 * 1024


def fail(msg):
    print(f"VALIDATION FAILED: {msg}")
    sys.exit(1)


def main(dist_dir):
    dist = Path(dist_dir)
    zips = list(dist.glob("firmware-*.zip"))
    if len(zips) != 1:
        fail(f"expected exactly one firmware zip, found {len(zips)}")
    zip_path = zips[0]
    version = zip_path.stem.replace("firmware-", "")

    if zip_path.stat().st_size > MAX_SIZE_BYTES:
        fail("firmware is larger than the allowed size")

    sha_file = dist / f"firmware-{version}.sha256"
    if not sha_file.exists():
        fail("checksum file missing")
    expected = sha_file.read_text().split()[0]
    actual = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if expected != actual:
        fail("checksum mismatch")

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        for required in ("meter.py", "version.txt"):
            if required not in names:
                fail(f"{required} missing from package")
        if z.read("version.txt").decode().strip() != version:
            fail("version.txt does not match package version")
        code = z.read("meter.py").decode()
        if f'VERSION = "{version}"' not in code:
            fail("version not stamped into meter.py")
        compile(code, "meter.py", "exec")  # syntax check

    print(f"OK: {zip_path.name} is valid (version {version})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist")
