"""Build the localized pages and the sitemap from src/index.html and i18n/*.json.

Usage: python tools/build.py   (run from anywhere; writes into the repo)

Each locale gets its own URL so search engines can index it. English is the root page.
Template syntax: {{ key }} inserts HTML-escaped text, {{ key | json }} writes a JSON
string, and {{ key | raw }} inserts HTML as is. Keys starting with "page." come from
this script; the rest come from the locale's JSON.
"""
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ohhnate.dev"
DEFAULT_CODE = "en"
METER_START_YEAR = 2012
PLACEHOLDER = re.compile(r"\{\{\s*([\w.]+)\s*(?:\|\s*(\w+)\s*)?\}\}")

# Fonts each script needs for its first paint. Chinese and Japanese draw body text in system fonts.
PRELOADS = {
    "latin": ("anybody-italic", "schibsted-grotesk"),
    "cyrillic": ("anybody-italic", "schibsted-grotesk"),
    "cjk": ("anybody-italic",),
}


@dataclass(frozen=True)
class Locale:
    code: str  # i18n file name and the value saved when a visitor picks a language
    html_lang: str
    hreflangs: tuple[str, ...]
    og_locale: str
    name: str  # the language's own name, shown in the language menu
    script: str  # a PRELOADS key
    aliases: tuple[str, ...] = ()  # extra lowercase browser tags that should land here

    @property
    def path(self) -> str:
        return "/" if self.code == DEFAULT_CODE else f"/{self.code}/"


# Browser tags match a locale by full tag, then alias, then base language. Chinese tags other
# than Hong Kong and Macau (including zh-TW) fall back to Mandarin, the first "zh" locale.
LOCALES = (
    Locale("en", "en-US", ("en",), "en_US", "English", "latin"),
    Locale("zh-cn", "zh-CN", ("zh-CN", "zh"), "zh_CN", "简体中文", "cjk"),
    Locale("zh-hk", "zh-HK", ("zh-HK",), "zh_HK", "廣東話", "cjk", ("zh-mo", "zh-hant-hk", "zh-hant-mo", "yue")),
    Locale("ja", "ja", ("ja",), "ja_JP", "日本語", "cjk"),
    Locale("es", "es", ("es",), "es_ES", "Español", "latin"),
    Locale("pt-br", "pt-BR", ("pt-BR", "pt"), "pt_BR", "Português (Brasil)", "latin"),
    Locale("de", "de", ("de",), "de_DE", "Deutsch", "latin"),
    Locale("fr", "fr", ("fr",), "fr_FR", "Français", "latin"),
    Locale("ru", "ru", ("ru",), "ru_RU", "Русский", "cyrillic"),
)


def load_strings() -> dict[str, dict[str, str]]:
    """Load every locale's strings and fail if any file's keys differ from English."""
    strings = {loc.code: json.loads((ROOT / "i18n" / f"{loc.code}.json").read_text(encoding="utf-8")) for loc in LOCALES}
    expected = set(strings[DEFAULT_CODE])
    problems = []
    for code, table in strings.items():
        missing, extra = expected - set(table), set(table) - expected
        if missing or extra:
            problems.append(f"{code}.json: missing {sorted(missing)}, extra {sorted(extra)}")
    if problems:
        sys.exit("Translation keys don't match en.json:\n  " + "\n  ".join(problems))
    return strings


def alternate_links() -> list[tuple[str, str]]:
    """Every (hreflang, URL) pair, ending with x-default for the language-detecting root."""
    pairs = [(tag, SITE + loc.path) for loc in LOCALES for tag in loc.hreflangs]
    return pairs + [("x-default", SITE + "/")]


def locale_paths() -> dict[str, str]:
    """Map locale codes, aliases and base languages to paths, for the root page's redirect script."""
    paths: dict[str, str] = {}
    for loc in LOCALES:
        paths[loc.code] = loc.path
        paths.setdefault(loc.code.split("-")[0], loc.path)
        paths.update(dict.fromkeys(loc.aliases, loc.path))
    return paths


def meter_months(today: date) -> int:
    """The meter's column for the current month; January of METER_START_YEAR is column 1."""
    return (today.year - METER_START_YEAR) * 12 + today.month


def lang_item(other: Locale, current: Locale) -> str:
    here = ' aria-current="true"' if other is current else ""
    return (
        f'\t\t\t\t\t<li><a href="{other.path}" hreflang="{other.html_lang}" lang="{other.html_lang}" '
        f'data-lang="{other.code}"{here}>{other.name}</a></li>'
    )


def asset_version(relative: str) -> str:
    """A short content hash for an asset URL, so a deploy never pairs new pages with a cached old file."""
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()[:10]


def shared_values(today: date) -> dict[str, str]:
    """Values that are the same on every page."""
    return {
        "page.months": str(meter_months(today)),
        "page.css": (ROOT / "styles.css").read_text(encoding="utf-8"),
        "page.js_version": asset_version("assets/site.js"),
        "page.locale_paths": json.dumps(locale_paths(), ensure_ascii=False),
        "page.hreflang_links": "\n".join(f'\t<link rel="alternate" hreflang="{tag}" href="{url}">' for tag, url in alternate_links()),
    }


def page_values(loc: Locale) -> dict[str, str]:
    return {
        "page.lang": loc.html_lang,
        "page.url": SITE + loc.path,
        "page.og_locale": loc.og_locale,
        "page.lang_name": loc.name,
        "page.lang_items": "\n".join(lang_item(other, loc) for other in LOCALES),
        "page.og_locale_alternates": "\n".join(
            f'\t<meta property="og:locale:alternate" content="{other.og_locale}">' for other in LOCALES if other is not loc
        ),
        "page.preloads": "\n".join(
            f'\t<link rel="preload" href="/assets/fonts/{font}.woff2" as="font" type="font/woff2" crossorigin>'
            for font in PRELOADS[loc.script]
        ),
    }


def render(template: str, values: dict[str, str]) -> str:
    def substitute(match: re.Match) -> str:
        key, mode = match.group(1), match.group(2) or "text"
        if key not in values:
            sys.exit(f"Template uses unknown key: {key}")
        value = values[key]
        if mode == "text":
            return html.escape(value)
        if mode == "json":
            return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")
        if mode == "raw":
            return value
        sys.exit(f"Unknown filter '{mode}' on {key}")

    return PLACEHOLDER.sub(substitute, template)


def write_sitemap() -> None:
    alternates = "".join(f'\n\t\t<xhtml:link rel="alternate" hreflang="{tag}" href="{url}"/>' for tag, url in alternate_links())
    urls = "".join(f"\n\t<url>\n\t\t<loc>{SITE}{loc.path}</loc>{alternates}\n\t</url>" for loc in LOCALES)
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        f"{urls}\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")


def main() -> None:
    template = (ROOT / "src" / "index.html").read_text(encoding="utf-8")
    strings = load_strings()
    shared = shared_values(date.today())
    for loc in LOCALES:
        out = ROOT / loc.path.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template, {**strings[loc.code], **shared, **page_values(loc)}), encoding="utf-8", newline="\n")
        print(f"wrote {out.relative_to(ROOT).as_posix()}")
    write_sitemap()
    unused = sorted(set(strings[DEFAULT_CODE]) - {key for key, _ in PLACEHOLDER.findall(template)})
    if unused:
        print(f"warning: strings no page uses: {unused}")


if __name__ == "__main__":
    main()
