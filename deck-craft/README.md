# deck-craft

A Claude skill for making PowerPoint (`.pptx`) decks that don't look AI-generated.

Instead of guessing, it asks a few questions, builds a fact ledger and a sentence-title outline, shows a **real rendered preview** of the design, then builds a native editable deck and **lints it for slop** (default fonts, accent lines under titles, flat backgrounds, label titles, invented numbers).

It is a design and process layer on top of Anthropic's built-in `pptx` skill, not a replacement for it.

## What you get

- **A guided flow:** intake (max 4 tappable questions) → fact ledger → outline → preview → build → checks → delivery.
- **A builder:** `tokens.json` + `content.json` → native, editable `.pptx`. Nine slide types: `title`, `statement`, `stat`, `split`, `compare`, `steps`, `quote`, `chart`, `closing`.
- **Four design systems:** `night-lab` (dark technical), `editorial-ink` (light, red accent), `field-green` (calm), `wildcard-terminal` (monospaced, acid lime).
- **A lint script:** mechanical design checks, no model tokens. Flags numbers not found in your fact ledger.
- **Helpers:** gradient/grain background generator, palette extractor for reference images, one-image contact-sheet renderer.
- **Editable source:** the deck ships with its token and content files, so "make it darker" is a token edit and a rebuild.

## Install

**claude.ai:** zip the `deck-craft/` folder (or use the packaged `deck-craft.skill`), then Settings → Capabilities → Skills → upload.

**Claude Code:**
```bash
git clone https://github.com/charansaiponnada/my-skills ~/.claude/skills/deck-craft
```
Restart the session. The skill name must match the folder name (`deck-craft`).

**Agent Skills CLI:**
```bash
npx skills add charansaiponnada/my-skills@deck-craft -g -y
```

## Use it

Just ask. It triggers on requests for a presentation, pitch deck, hackathon/demo-day deck, research talk or project walkthrough as PowerPoint, especially when you mention style, a reference or "not generic".

Example prompts:
- "Make a 6-slide hackathon pitch deck for my credit-risk project. Dark and technical."
- "Build a research talk deck from this abstract. Here's a screenshot of the look I want."
- "Make this deck look designed, not like AI. Here's my outline."

Say how much effort you want: **Quick** (no question round), **Standard** (default, with preview), **Deep** (two design directions and a closer review).

## How the checks work

```bash
python scripts/lint_deck.py deck.pptx --facts facts.json   # errors fail with exit code 1
python scripts/lint_deck.py deck.pptx --brand              # brand template: style bans off
python scripts/lint_deck.py deck.pptx --json               # machine-readable
python scripts/preview.py deck.pptx sheet.png --cols 3     # one contact-sheet image
```
Lint rules and their replacements: `references/slop-list.md`.

## Folder layout

```
deck-craft/
├── SKILL.md                 workflow and hard rules (what Claude reads)
├── README.md                this file
├── references/              builder schema, design systems, recipes, story rules, slop list
├── scripts/                 build_deck.js, lint_deck.py, make_background.py,
│                            extract_palette.py, preview.py
└── assets/                  example content and four design-system token files
```

## Requirements

- Node with `pptxgenjs`; Python 3 with `python-pptx`, `Pillow`, `numpy`
- LibreOffice and `pdftoppm` (Poppler) for previews
- Anthropic's `pptx` skill: `build_deck.js` uses its `apply_theme.js`, `preview.py` its `soffice.py` wrapper, and the workflow uses its `validate.py`. If it is installed somewhere other than `/mnt/skills/public/pptx`, set `PPTX_SKILL_DIR`.

Tested in the claude.ai sandbox. Other setups may need path tweaks, so open an issue if something breaks.

## Customize

- **Add a design system:** copy a file in `assets/systems/`, change colors and fonts, check contrast on both dark and light slides.
- **Add a slide type:** add a function to `BUILD` in `scripts/build_deck.js`; document it in `references/builder.md`.
- **Keep the slop list current:** when you spot a new tell in your own output, add a dated row to `references/slop-list.md`.

## Limitations

- Fonts can't be identified from an image. The skill maps to the closest safe font and says so.
- Lint catches mechanical tells, not taste. Look at the contact sheet.
- No photo, table or equation slide types yet (see `references/builder.md`).
- Design systems are dated 2026-11 and will feel familiar eventually. Refresh them.

## Publish your own copy

```bash
cd deck-craft
git init && git add . && git commit -m "deck-craft v0.1"
git branch -M main
git remote add origin git@github.com:<you>/deck-craft.git
git push -u origin main
```
Then set the repo to **Public** in GitHub settings.

## License

MIT. See `LICENSE`. Replace the copyright line with your name.
