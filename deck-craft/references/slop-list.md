# Slop tells (dated 2026-11). Every ban has a replacement. Re-derive when outputs start to look samey.

A ban list removes the floor; it doesn't build a ceiling. Pair it with the story rules and a real design system. Some bans are proxies for "reached for the default and stopped thinking": enforce strictly in the skill, hold loosely in review. A brand template or guide outranks this list.

| Tell | Why it reads as AI | Instead | Lint rule |
|---|---|---|---|
| Inter / Roboto / Aptos / Open Sans / all-Arial | no font choice was made | safe serif or mono heading + Calibri | `banned-font`, `default-fonts` |
| Thin line under the title | most-cited generation tell | whitespace, a tint change | `rule-line` |
| Full-width header/footer bars, edge stripes on cards | decorative filler | a subtle tint, or nothing | `color-bar`, `stripe` |
| Flat white/solid backgrounds on every slide | no atmosphere | gradient + grain PNG | `flat-backgrounds` |
| Evenly weighted palette, default blue | "timid" | one dominant + one sharp accent, topic-specific | (design systems) |
| Topic-label titles ("Overview", "Results") | no point made | sentence takeaway | `label-title` |
| Identical 3-card grids and icon-in-circle rows | template filler | big numbers, flows, charts; vary layouts | `repeat-layout`, `low-variety` |
| Text-only slides | forgettable | a chart, shape, or oversized number | `no-visual` |
| Wall of bullets, tiny text | unreadable live | cut words, >= 14pt | `dense-slide`, `small-body`, `tiny-text` |
| Invented stats and "10x faster" claims | fabricated | ledger-only numbers or `[TBD]` | `unverified-number` |
| "Thank you / Questions?" ending | no next step | a decision or ask | (story rules) |
| Workflow leaks: "Option A", template names | internal text on a slide | never | `placeholder-text` |
| Title position or size drifting between slides | sloppy system | placeholders from one layout | `title-drift` |
| Beige/cream default backgrounds | warm-neutral default | white or a designed gradient | (design systems) |
| Heavy drop shadows and rounded pills everywhere | decoration over information | flat tints, restraint | (review) |

## Keeping this list honest
When you spot a new tell in your own output, add a row with the date and a replacement. Delete rows that no longer apply.
