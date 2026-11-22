# Builder schema (`scripts/build_deck.js`)

`node build_deck.js tokens.json content.json out.pptx [--preview]`
Needs `pptxgenjs`, Python with Pillow + numpy (backgrounds), and the pptx skill's `apply_theme.js` (override the location with `PPTX_SKILL_DIR`).
Canvas is 10 x 5.625 in. Colors are hex without `#`.

## tokens.json
```json
{
  "name": "night-lab",
  "fonts":  { "heading": "Cambria", "body": "Calibri" },
  "colors": {
    "ink": "0B1020", "paper": "FFFFFF", "muted": "5B6480",
    "accent": "3DDCFF",           // accent on DARK slides
    "accent_on_light": "0B7FA3",  // darker accent for LIGHT slides (contrast!)
    "accent2": "FFB454",
    "on_dark": "F1F4FB", "on_dark_muted": "9AA4C7",
    "card_light": "EEF1F8", "card_dark": "1B2347",
    "dark_bg": ["0B1020", "182044"], "light_bg": ["FFFFFF", "EEF1F8"]
  },
  "glow":  { "x": 0.88, "y": 0.08, "color": "3DDCFF", "radius": 0.55, "strength": 0.28 },
  "grain": 0.02, "angle": 135,
  "sizes": { "title": 36, "cover": 46, "statement": 40, "quote": 32, "perLine": 32 }
}
```
`sizes.perLine` is the approximate characters per title line; the builder warns when a title would wrap past 3 lines. Wide faces (Courier New) need smaller sizes and a smaller `perLine`.
Check contrast: `accent` on a dark background and `accent_on_light` on a white one must both be readable.

## content.json
```json
{ "title": "Deck name", "author": "Name", "slides": [ { "type": "...", "notes": "speaker notes" } ] }
```
`theme: "dark" | "light"` on any slide overrides its default. Titles lose a trailing period automatically.

| type | default | fields | limits |
|---|---|---|---|
| `title` | dark | `kicker`, `title`, `subtitle`, `meta` | one cover |
| `statement` | dark | `title` (one big sentence), `emphasis` (substring to color), `support` | title <= ~100 chars |
| `stat` | light | `title`, `stats: [{value, label, note}]` | 1 to 3 stats; keep values short ("94.2%") |
| `split` | light | `title`, `bullets[]`, optional `callout_label`, `callout` | <= 4 bullets; callout adds a card |
| `compare` | light | `title`, `columns: [{heading, bullets[]}]` | exactly 2 columns, <= 4 bullets |
| `steps` | light | `title`, `steps: [{title, text}]` | 3 to 4 steps |
| `quote` | dark | `title` (the quote), `attribution` | real quotes only |
| `chart` | light | `title`, `chart: {type: bar or line, labels[], series: [{name, values[]}]}`, `takeaway`, `source` | native editable chart |
| `closing` | dark | `title`, `points[]`, `contact` | <= 3 points |

## Not covered (add deliberately)
- Photos or screenshots: `slide.addImage({path, x, y, w, h})` in a new `BUILD` function; give each image alt text.
- Tables, equations, diagrams: add a builder function; keep native objects where PowerPoint has one.
- Code: monospace text box, >= 12pt.
- Template-based decks: don't use this builder. Edit the template per the pptx skill and lint with `--brand`.
