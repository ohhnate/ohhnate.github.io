# ohhnate.dev

Portfolio site for Nate Fuller, served by GitHub Pages at https://ohhnate.dev. Static HTML and CSS with a little JavaScript for the theme toggle and language menu.

## Building

The pages are generated. Edit `src/index.html` (the template) and `i18n/*.json` (the text), never the generated `index.html` files, then run:

    python tools/build.py

It writes `index.html` (English) and one `<locale>/index.html` per language, plus `sitemap.xml` with `hreflang` alternates for every page. It stops if a language file is missing a key or has an extra one, and warns about strings the template no longer uses. Commit the generated files; GitHub Pages serves them as they are.

To preview locally, serve the folder (asset paths are root-relative): `python -m http.server`, then open http://localhost:8000.

The build stamps the stylesheet and script URLs with a content hash (`styles.css?v=…`), so a deploy never pairs new pages with a cached old stylesheet.

## Search engines

After a deploy that changes content, run `python tools/indexnow.py` to notify Bing, Yandex and the other IndexNow engines. It needs the key file at the repo root (the 32-character hex `.txt` file), so keep that file. Google reads `sitemap.xml` through Search Console.

## Languages

English, Mandarin (Simplified, `/zh-cn/`), Cantonese (Traditional, `/zh-hk/`), Japanese, Spanish, Brazilian Portuguese, German, French and Russian, configured in `LOCALES` in `tools/build.py`.

On the root URL, a small script in `<head>` sends first-time visitors to the version that matches their browser language, or to the language they picked before from the menu. Every other URL stays where it is, so search engines and shared links always get the page they asked for.

The non-English text was machine-drafted and should be checked by a fluent reader before anything else relies on it.

## The frame meter

The hero meter has one column per month from January 2012. The build sets the column count from the current date, so rebuilding is all a new month needs. To add an era, give its `<i>` segment `--from` (the first month's column, `(year - 2012) * 12 + month`) and `--span` (how many months it covers), plus a `.meter-label` with the same `--from`. The current era has the `ongoing` class and no `--span`, so it runs to the end.

## When the job changes

Update the hero and Experience strings in every `i18n/*.json`, the meter in `src/index.html`, the era cells in the logo (in `src/index.html` and the hand-written `404.html`), and `assets/og.png`, a language-neutral 1200x630 screenshot of the name and the meter.

## Fonts

Self-hosted and trimmed by `tools/trim_fonts.py` (instructions at the top of the script); the license texts are in `assets/fonts/`. Chinese and Japanese use system fonts.

## Images

Each game cover has a half-size `-315` copy and the Idol Showdown shot a `-640` copy, both plain Pillow resizes that the `srcset` attributes choose between. New images need the same.
