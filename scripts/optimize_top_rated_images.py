#!/usr/bin/env python3
"""Resize and compress img1–img12 for the Top Rated grid (web performance)."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "static" / "images" / "enhanced-images"
MAX_EDGE = 900
JPEG_QUALITY = 82


def optimize(path):
    before = path.stat().st_size
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        im.save(
            path,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )
    after = path.stat().st_size
    return before, after


def main() -> None:
    total_before = total_after = 0
    for i in range(1, 13):
        path = IMG_DIR / f"img{i}.jpeg"
        if not path.is_file():
            print(f"skip missing: {path.name}")
            continue
        b, a = optimize(path)
        total_before += b
        total_after += a
        print(f"{path.name}: {b // 1024}KB -> {a // 1024}KB")
    print(f"Total: {total_before // 1024}KB -> {total_after // 1024}KB")


if __name__ == "__main__":
    main()
