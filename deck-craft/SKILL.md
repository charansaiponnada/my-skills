---
name: deck-craft
description: Design-led PowerPoint (.pptx) decks that don't look AI-generated. Interviews the user (purpose, audience, references, mood), builds a fact ledger and a sentence-title outline, shows a real rendered preview of the design, then builds a native editable deck and lints it for slop (default fonts, accent lines, flat backgrounds, label titles, invented numbers). Use whenever the user wants a presentation, slide deck, pitch deck, hackathon/demo-day deck, research talk or project walkthrough as a PowerPoint/.pptx, and especially when they mention design, style, a reference deck/screenshot, "not generic", "no AI slop", or "make it look good". Works on top of the pptx skill. Make sure to use this for any new .pptx deck that someone will present to other people, even if they never mention design.
---

# deck-craft

A design and process layer on top of the built-in **pptx** skill. The pptx skill knows how to write a valid file. This skill decides what the deck should say, how it should look, and checks the result without spending model tokens on eyeballing.

**First:** read `/mnt/skills/public/pptx/SKILL.md` (gotchas, `validate.py`, render commands). If the session offers a Slides artifact type and the user did not ask for a `.pptx`, follow the pptx skill's rule and use that instead.

Paths below use `<skill>` for this skill's folder.

## Why decks look like slop
Claude guesses the audience, mood and message, then falls back to the average look. So: ask, reference, preview, then check mechanically. Every step below exists to remove a guess.

## 1. Pick a mode (say it in one line)
| Mode | When | Steps |
|---|---|---|
| **Quick** | internal, throwaway, user says "just make it" | 1 to 3 (no question round), build, lint, one contact-sheet look |
| **Standard** (default) | pitches, talks, anything presented | all steps |
| **Deep** | finals, funding, "make it perfect" | Standard + two design directions + per-slide look at flagged slides |

## 2. Intake (one round, max 4 questions, skip what the prompt already answers)
Use `ask_user_input_v0` (tappable) when available. Every question needs a "your best guess" option.
1. **Purpose and audience**: pitch / research talk / project walkthrough / intro / report. How many minutes? (slides ≈ minutes ÷ 1.5 to 2)
2. **Reference**: screenshot, link, old deck, brand colors? If given, skip question 3.
3. **Mood**: dark technical / light editorial / calm & grounded / bold & unusual.
4. **Source material**: do they have the content, or is it only a topic? If only a topic, content is placeholder: write `[TBD: ...]` markers, never invented figures.

Reference handling: image → `python <skill>/scripts/extract_palette.py ref.png` (palette is reliable; **fonts cannot be read from an image**, map to the closest safe font and say so). `.pptx` → same script reads the theme exactly. Brand template or mandated brand look → edit from the template per the pptx skill and lint with `--brand`.

## 3. Fact ledger (prevents invented numbers)
Write `facts.json`: `{"facts": ["Beat baseline by 12 points", "AUC 94.2%"], "numbers": []}` from what the user actually gave. Every number on a slide must trace to it. No ledger entry means `[TBD]`, not a plausible guess.

## 4. Outline, then tokens
- **Outline** = one line per slide, each a full-sentence takeaway ("Our model beat the baseline by 12 points", not "Results"). One message per slide. Pick the skeleton from `references/recipes.md`. Rules in `references/story-rules.md`.
- **Tokens**: copy a system from `assets/systems/` (night-lab, editorial-ink, field-green, wildcard-terminal) or derive from the reference. See `references/design-systems.md`. Write `tokens.json` and `content.json` (schema: `references/builder.md`).

## 5. Preview (Standard and Deep)
Build only the cover plus one real content slide with the same code as the final deck, then show **one image**:
```
node <skill>/scripts/build_deck.js tokens.json content.json preview.pptx --preview
python <skill>/scripts/preview.py preview.pptx preview.png --cols 2 --dpi 70
```
Show the image and the numbered outline together. Ask for a pick or one change. Deep mode: build a second preview from a different system (include the wildcard) and show both. If they dislike it, ask one question ("what feels off: color, density, or tone?"), change those tokens only, re-preview once.

## 6. Build
```
node <skill>/scripts/build_deck.js tokens.json content.json deck.pptx
```
Output is native and editable (text, charts, shapes); only the two background PNGs are images. Variety is built in: nine slide types, so don't use one type twice in a row. For a slide type the builder lacks, copy `build_deck.js`, add a function to `BUILD`, and keep the same token rules. Speaker notes go in `notes`.

## 7. Gates (scripts do the checking, not your eyes)
```
python <skill>/scripts/lint_deck.py deck.pptx --facts facts.json      # add --json to parse, --brand for template decks
python /mnt/skills/public/pptx/scripts/office/validate.py deck.pptx
python <skill>/scripts/preview.py deck.pptx sheet.png --cols 3 --dpi 60  # ONE contact sheet
```
- Fix every **error**. Read each **warning**; fix or consciously accept.
- Look at the contact sheet once. Open a single slide (`--slide N --dpi 120`) only when lint or the sheet points at it.
- **One fix pass, then stop.** Do not loop. List what is still weak in the reply.

## 8. Deliver
Copy `deck.pptx`, `tokens.json`, `content.json` to `/mnt/user-data/outputs/` and `present_files` them (the JSON pair means "make it darker" is a token edit and rebuild, not a patch job). Reply in 3 to 5 lines: assumptions made, anything flagged (`[TBD]` markers, unverified numbers), and the one change you'd try next.

## Hard rules (mechanical, each with a replacement)
- No default-font look: not Inter/Roboto/Aptos/Open Sans. Use a pairing from `references/design-systems.md` (safe serif heading + Calibri).
- No accent line under titles, header/footer bars, edge stripes. Use whitespace or a tint change.
- No flat single-color backgrounds across the deck. Use `make_background.py` gradient/grain PNGs.
- Titles are sentences, no trailing period. Body 14pt or more, captions 10pt or more.
- Never the same layout twice in a row. One dominant color plus one sharp accent.
- No invented numbers, names or quotes. No workflow leaks on slides ("Option A", template names).
- A brand template or guide outranks every style rule above. Lint with `--brand`.

Full dated list with replacements: `references/slop-list.md`. Re-derive it when outputs start to look samey.

## Token discipline
Scripts report, images are expensive: one contact sheet, not N slides. One preview, not three, unless Deep. Skill references load only when needed.
