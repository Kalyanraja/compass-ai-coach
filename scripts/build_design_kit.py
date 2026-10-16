"""Zip design-kit/ into downloads/compass-design-kit.zip (deterministic order).

Usage: python scripts/build_design_kit.py
"""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "design-kit"
OUT = ROOT / "downloads" / "compass-design-kit.zip"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SRC.rglob("*") if p.is_file())
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo("compass-design-kit/" + p.relative_to(SRC).as_posix(), date_time=(2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    print(f"wrote {OUT.relative_to(ROOT)} with {len(files)} files, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
