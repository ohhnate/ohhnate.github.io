"""Trim the site's web fonts to the axis ranges and characters styles.css uses.

Each family is split by character set so pages only download what they show:
"core" (ASCII and common punctuation, preloaded), "ext" (accented Latin for the
European locales) and "cyrillic" (Russian, from a matching family). Chinese and
Japanese use system fonts.

Get the sources from Google Fonts: request each CSS URL below with a desktop Chrome
user agent and download the woff2 under the named subset comment.

  latin:    https://fonts.googleapis.com/css2?family=Anybody:ital,wdth,wght@1,50..150,100..900&family=Schibsted+Grotesk:wght@400..900
  cyrillic: https://fonts.googleapis.com/css2?family=Fira+Sans+Extra+Condensed:ital,wght@1,800&family=Golos+Text:wght@400..700

Save them as Anybody-latin.woff2, SchibstedGrotesk-latin.woff2,
FiraSansExtraCondensed-cyrillic.woff2 and GolosText-cyrillic.woff2, then run:

  pip install fonttools brotli
  python tools/trim_fonts.py <folder with the downloads> assets/fonts

The script prints each output's unicode-range; the @font-face blocks in styles.css
must use the same ranges and the same axis ranges as AXES below.
"""
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# Core carries « » too: the Russian page uses them, and that keeps it off the "ext" files.
CORE = list(range(0x20, 0x7F)) + [
    0xA0, 0xA9, 0xAB, 0xBB, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026, 0x2122,
]
CHARSETS = {
    "core": CORE,
    "ext": [cp for cp in range(0xA0, 0x100) if cp not in CORE] + [0x152, 0x153, 0x202F, 0x2039, 0x203A, 0x20AC],
    "cyrillic": list(range(0x400, 0x460)) + [0x490, 0x491, 0x2116],
}

ANYBODY_AXES = {"wdth": (58, 80), "wght": (800, 850)}
SCHIBSTED_AXES = {"wght": (400, 700)}

# (source file, output file, charset, axis ranges or None for a static font)
FONTS = [
    ("Anybody-latin.woff2", "anybody-italic.woff2", "core", ANYBODY_AXES),
    ("Anybody-latin.woff2", "anybody-italic-ext.woff2", "ext", ANYBODY_AXES),
    ("SchibstedGrotesk-latin.woff2", "schibsted-grotesk.woff2", "core", SCHIBSTED_AXES),
    ("SchibstedGrotesk-latin.woff2", "schibsted-grotesk-ext.woff2", "ext", SCHIBSTED_AXES),
    ("FiraSansExtraCondensed-cyrillic.woff2", "fira-sans-extra-condensed-cyrillic.woff2", "cyrillic", None),
    ("GolosText-cyrillic.woff2", "golos-text-cyrillic.woff2", "cyrillic", SCHIBSTED_AXES),
]


def unicode_range(codepoints: list[int]) -> str:
    """Collapse code points into a CSS unicode-range value."""
    runs, start = [], None
    points = sorted(codepoints)
    for i, cp in enumerate(points):
        if start is None:
            start = cp
        if i + 1 == len(points) or points[i + 1] != cp + 1:
            runs.append(f"U+{start:04X}" if start == cp else f"U+{start:04X}-{cp:04X}")
            start = None
    return ", ".join(runs)


def trim(src: Path, out: Path, codepoints: list[int], axes: dict | None) -> None:
    font = TTFont(src)
    options = Options()
    # Keep every OpenType feature; the defaults drop tnum, which the year labels use.
    options.layout_features = ["*"]
    subsetter = Subsetter(options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)
    if axes:
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
    for src_name, out_name, charset, axes in FONTS:
        trim(src_dir / src_name, out_dir / out_name, CHARSETS[charset], axes)
    for name, codepoints in CHARSETS.items():
        print(f"{name} unicode-range: {unicode_range(codepoints)};")


if __name__ == "__main__":
    main()
