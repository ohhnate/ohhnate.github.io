# ohhnate.dev

Portfolio site for Nate Fuller, served by GitHub Pages at https://ohhnate.dev. Plain HTML and CSS with no build step.

## Updating the frame meter

The hero meter has one column per month, starting at January 2012. A month's column is `(year - 2012) * 12 + month`.

- Each month, set `--months` on `<figure class="meter">` in `index.html` to the current month's column. The current segment has the `ongoing` class and no `--span`, so it always runs to the end.
- To add an era, give the new `<i>` segment `--from` (its first month's column) and `--span` (how many months it covers), plus a `.meter-label` with the same `--from`.

## When the job changes

Update the hero intro, the Experience list, the meter, the meta description in `<head>`, and `assets/og.png`. The link preview is a 1200x630 screenshot of the name, the tagline and the meter, so it only needs remaking when an era changes.

## Fonts

Anybody and Schibsted Grotesk (SIL Open Font License, texts in `assets/fonts/`) are self-hosted and trimmed to the characters and axis ranges the site uses. The ranges in the `@font-face` blocks in `styles.css` must match `tools/trim_fonts.py`. To use a new weight, width or character, follow the instructions at the top of that script.

## Images

Each game cover has a half-size `-315` copy and the Idol Showdown shot a `-640` copy, both plain Pillow resizes that the `srcset` attributes choose between. New images need the same.
