"""Make the site's WebP images from the original downloads.

Usage: python tools/make_images.py <folder with the originals> assets

Pixel art is downscaled with nearest-neighbor and saved lossless, which keeps it crisp and
is several times smaller than lossy WebP for flat-color art. Photos and painted art are
resampled with Lanczos and saved lossy. Every width listed here must also appear in the
matching srcset in src/index.html.

Originals: the Idol Showdown Steam screenshot (idol8.jpg) and each itch.io page's cover
image ("original" size, linked from the page's og:image tag).
"""
import sys
from pathlib import Path

from PIL import Image

LOSSY_QUALITY = 75
COVER_RATIO = 630 / 500
SHOT_RATIO = 16 / 9

# (source file, output name, aspect ratio, pixel art?, {width: output suffix})
IMAGES = [
    ("idol8.jpg", "idol-showdown", SHOT_RATIO, False, {1280: "", 960: "-960", 720: "-720", 640: "-640"}),
    ("foxtales.png", "foxtales", COVER_RATIO, True, {630: "", 315: "-315"}),
    ("baubau.png", "bau-bau-bustin-out", COVER_RATIO, False, {630: "", 315: "-315"}),
    ("lightless.png", "lightless", COVER_RATIO, False, {630: "", 315: "-315"}),
    ("carrot.png", "carrot-catcher", COVER_RATIO, True, {630: "", 315: "-315"}),
]


def crop_to_ratio(im: Image.Image, ratio: float) -> Image.Image:
    w, h = im.size
    if w / h > ratio:
        new_w = round(h * ratio)
        left = (w - new_w) // 2
        return im.crop((left, 0, left + new_w, h))
    new_h = round(w / ratio)
    top = (h - new_h) // 2
    return im.crop((0, top, w, top + new_h))


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: make_images.py <source_dir> <out_dir>")
    src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    for source, name, ratio, pixel_art, widths in IMAGES:
        base = crop_to_ratio(Image.open(src_dir / source).convert("RGB"), ratio)
        for width, suffix in widths.items():
            size = (width, round(width / ratio))
            out = out_dir / f"{name}{suffix}.webp"
            if pixel_art:
                base.resize(size, Image.NEAREST).save(out, "WEBP", lossless=True, method=6)
            else:
                base.resize(size, Image.LANCZOS).save(out, "WEBP", quality=LOSSY_QUALITY, method=6)
            print(f"{out.name}: {size[0]}x{size[1]}, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
