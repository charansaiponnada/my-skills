# Design systems (dated 2026-11; replace when they start to feel familiar)

Ready-made token files live in `assets/systems/`. Pick by context, don't mix.

| System | Feels like | Use for | Fonts |
|---|---|---|---|
| `night-lab` | dark, technical, one cyan glow | AI/ML demos, research talks, dev tools | Cambria + Calibri |
| `editorial-ink` | high-contrast magazine, one hot red | pitches, reports, argument-led talks | Century Schoolbook + Calibri |
| `field-green` | calm, grounded, deep green + lime | health, sustainability, education, community | Bookman Old Style + Calibri |
| `wildcard-terminal` | monospaced headings, acid lime | hackathons, demo days, dev-tool launches | Courier New + Calibri |

Standard mode: propose the best fit. Deep mode: show that one plus the wildcard, so the options don't converge.

## Why these fonts
Fonts you write into a `.pptx` are rendered by the viewer's PowerPoint. Web fonts fall back to Arial on other machines, which is worse than a good safe pairing. All four systems use fonts that ship with Office and render true-to-width in QA. Personality comes from the serif/mono heading plus size contrast, not from exotic font files.

## Deriving a system from a reference
1. `extract_palette.py` gives background, text, accent roles. Use them as `dark_bg`/`light_bg`, `ink`, `accent`.
2. Make a second, darker shade of the accent for light slides (`accent_on_light`), and check contrast.
3. Copy the reference's habits, not its pixels: dark vs light, dense vs airy, big numbers vs prose, serif vs sans.
4. Map its fonts to the closest safe pair and say so. A geometric sans maps to Calibri body plus a serif or mono heading for contrast.
5. If the reference is a brand guide, the brand wins: lint with `--brand`.

## Rules that hold in every system
One dominant color (60 to 70% of visual weight), one supporting tone, one sharp accent. Title 34 to 46pt, body 14 to 16pt, captions >= 10pt. 0.5 in minimum margins, one consistent gap size. Backgrounds are gradient/grain PNGs, never flat. No accent lines or bars.
