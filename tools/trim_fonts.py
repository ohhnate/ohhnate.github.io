"""Trim the site's variable fonts to the axis ranges and characters styles.css uses.

Get the source files from Google Fonts: request the CSS below with a desktop Chrome
user agent and download the woff2 URL under each family's "latin" comment.

  https://fonts.googleapis.com/css2?family=Anybody:ital,wdth,wght@1,50..150,100..900&family=Schibsted+Grotesk:wght@400..900

Save them as Anybody-latin.woff2 and SchibstedGrotesk-latin.woff2, then run:

  pip install fonttools brotli
  python tools/trim_fonts.py <folder with the downloads> assets/fonts

If styles.css starts using a weight or width outside AXES, widen the range here,
rerun, and update the matching @font-face ranges.
"""
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# ASCII plus the typographic characters the copy uses. Add code points here if the
# copy needs others (accented letters, for example), then rerun.
UNICODES = list(range(0x20, 0x7F)) + [
    0xA0, 0xA9, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x2122,
]

FONTS = [
    ("Anybody-latin.woff2", "anybody-italic.woff2", {"wdth": (58, 80), "wght": (800, 850)}),
    ("SchibstedGrotesk-latin.woff2", "schibsted-grotesk.woff2", {"wght": (400, 700)}),
]


def trim(src: Path, out: Path, axes: dict) -> None:
    font = TTFont(src)
    options = Options()
    # Keep every OpenType feature; the defaults drop tnum, which the year labels use.
    options.layout_features = ["*"]
    subsetter = Subsetter(options)
    subsetter.populate(unicodes=UNICODES)
    subsetter.subset(font)
    # Instance after subsetting: the instancer drops glyph variations the subsetter expects.
    font = instantiateVariableFont(font, axes)
    font.flavor = "woff2"
    font.save(out)
    print(f"{out.name}: {src.stat().st_size // 1024} KB -> {out.stat().st_size // 1024} KB")


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: trim_fonts.py <source_dir> <out_dir>")
    src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for src_name, out_name, axes in FONTS:
        trim(src_dir / src_name, out_dir / out_name, axes)


if __name__ == "__main__":
    main()
