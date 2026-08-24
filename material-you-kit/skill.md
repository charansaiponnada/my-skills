---
name: material-design-3
description: Use this skill whenever the user wants to build, redesign, restyle, or "clean up" a UI using Google's Material Design 3 (M3 / "Material You") — for web (React/MUI, plain HTML/CSS, Vue) or mobile (Flutter, Jetpack Compose). Trigger on phrases like "material design", "M3", "material you", "redesign this UI", "use MUI/Material UI", "make this look like a Google app", or any request to apply Material components, color tokens, typography scale, or elevation to an existing or new interface. Also trigger when the user shares a screenshot or component and wants it converted to Material 3 styling. Covers component selection, the M3 color/type/shape/elevation token system, and stack-specific implementation (MUI v6, Material Web Components, Flutter, Jetpack Compose, or hand-rolled CSS tokens).
---

# Material Design 3 (M3)

A skill for designing and building interfaces that are authentically Material Design 3 — not "Bootstrap with rounded corners," not a random component kit, but the real M3 system: its color-role tokens, type scale, shape scale, elevation levels, and state layers, applied consistently through real Material components.

This skill covers two jobs, which the user's request will tell you between:

1. **Redesign** — take an existing UI (code, screenshot, or description) and re-express it in M3, replacing ad-hoc styling with M3 tokens and swapping generic elements for the correct M3 components.
2. **Build from scratch** — design a new screen/flow using M3 components and tokens from the start.

Both jobs use the same underlying knowledge (Section 2 and 3 below); they differ only in whether you're starting from existing markup or a blank file.

---

## 1. Figure out the stack first

Before writing anything, determine the target platform. If the user's message and any uploaded/attached code make it obvious, don't ask — just proceed. Only ask if genuinely ambiguous (e.g., a bare request with no code and no stack mentioned).

| Signal in the request | Stack | Reference file |
|---|---|---|
| React, `.jsx`/`.tsx`, "MUI", "Material UI", package.json with `@mui/material` | React + MUI v6 | `references/web-mui.md` |
| Plain `.html`/`.css`, "no framework", "vanilla" | Web Components (`@material/web`) or hand-rolled CSS tokens | `references/web-html-css.md` |
| Flutter, `.dart`, `pubspec.yaml` | Flutter (Material 3 is opt-in via `useMaterial3: true`) | `references/flutter.md` |
| Android, Kotlin, "Jetpack Compose", `.kt` | Jetpack Compose Material 3 (`androidx.compose.material3`) | `references/android-compose.md` |
| Vague / "web or mobile, whatever works" / no code given | Default to **React + MUI** for an artifact/demo unless the user corrects you | `references/web-mui.md` |

Read only the reference file(s) you need — don't load all four into context for a single-stack task. If the task spans two stacks (e.g., "redesign our web app and our Flutter app to match"), read both relevant files.

---

## 2. The M3 system (stack-agnostic — always apply this, regardless of stack)

Material 3 is not a component skin. Skipping any one of these four layers is why a "Material redesign" ends up looking like generic rounded-corner Bootstrap. Apply all four:

### a. Color roles, not hex codes
M3 color is defined by **roles**, generated from one or more seed colors via a tonal palette (13 tones per hue, 0=black, 100=white). Never hardcode a hex value for a UI surface, a button fill, or text — reference the role.

Core roles (each has a paired `on-` role for content that sits on top of it):
- `primary` / `on-primary` / `primary-container` / `on-primary-container`
- `secondary` / `on-secondary` / `secondary-container` / `on-secondary-container`
- `tertiary` / `on-tertiary` / `tertiary-container` / `on-tertiary-container`
- `error` / `on-error` / `error-container` / `on-error-container`
- `surface` / `on-surface` / `on-surface-variant`
- `surface-dim` / `surface-bright`
- `surface-container-lowest` / `-low` / (`-container`) / `-high` / `-highest` (5-step elevation-by-tint scale — M3 uses tonal surfaces instead of drop shadows for most elevation)
- `outline` / `outline-variant`
- `inverse-surface` / `inverse-on-surface` / `inverse-primary`

If the user gave a brand color, treat it as the seed and derive the rest — don't ask them to supply all 20+ roles manually. If they gave nothing, use a reasonable seed (their existing primary brand color if visible in the code/screenshot, otherwise a sensible default) and say what you picked.

### b. Type scale
Five size tiers × three levels each = 15 named styles. Use the named style, not an arbitrary `font-size`:

| Tier | Levels |
|---|---|
| Display | Large / Medium / Small — hero numbers, splash text |
| Headline | Large / Medium / Small — section headers |
| Title | Large / Medium / Small — card titles, dialog titles |
| Body | Large / Medium / Small — paragraph text |
| Label | Large / Medium / Small — buttons, chips, captions |

### c. Shape scale
Corner radius is tokenized, not per-component guesswork: `none` (0), `extra-small` (4dp), `small` (8dp), `medium` (12dp), `large` (16dp), `extra-large` (28dp), `full` (pill/circle). Match the token to the component's default (see component table in each reference file) rather than picking a radius that "looks right."

### d. Elevation via tone, not just shadow
M3 has 5 elevation levels (0–5). On light surfaces this is mostly a subtle drop shadow; M3's real innovation is that **elevated surfaces also shift to a slightly higher-tint surface-container role** (e.g. a resting card sits on `surface-container-low`, a modal on `surface-container-high`) rather than relying on shadow alone. Don't just add `box-shadow` and call it M3 — set the surface tone too.

### e. State layers
Interactive states (hover/focus/pressed/dragged) are a semi-transparent overlay of the content color at fixed opacities (hover ~8%, focus ~10%, pressed ~10-12%, dragged ~16%) on top of the resting color — not a separate hardcoded "hover color." Stack-specific components (MUI, Compose, Flutter) implement this automatically; only hand-roll it in the vanilla CSS/Web Components path.

---

## 3. Component inventory

Use this to pick the *right* M3 component instead of a generic `<div>`/`<button>` — the reference file for your stack gives the exact import/API for each:

- **Actions**: buttons (elevated / filled / filled tonal / outlined / text), icon buttons, FAB (small / regular / large / extended), segmented buttons
- **Communication**: badges, progress indicators (linear / circular, determinate / indeterminate), snackbar, tooltip
- **Containment**: cards (elevated / filled / outlined), dialogs, bottom sheet, side sheet, divider, list
- **Navigation**: top app bar (small / center-aligned / medium / large), bottom app bar, navigation bar (mobile, 3-5 destinations), navigation rail (tablet), navigation drawer (desktop/large screens), tabs
- **Selection**: checkbox, chip (assist / filter / input / suggestion), date picker, time picker, radio button, slider, switch
- **Text inputs**: text field (filled / outlined), search bar/view, menu (dropdown/exposed)
- **Other**: carousel

**Responsive rule of thumb** (applies across stacks): navigation bar on compact/mobile widths → navigation rail on medium/tablet widths → navigation drawer on expanded/desktop widths. Don't leave a mobile nav bar on a desktop layout in a "redesign" task — that's exactly the kind of half-applied M3 that looks wrong.

---

## 4. Workflow

**Redesign task:**
1. Identify the stack (Section 1).
2. Read the current code/screenshot. List every UI element and what M3 component it should become (a `<div className="card">` → M3 `Card` with the right variant; a colored `<button>` → the right M3 button variant based on its emphasis in the hierarchy — primary action = filled, secondary = outlined/tonal, low-emphasis = text).
3. Pick or derive the seed color(s) (Section 2a). State the choice.
4. Rewrite using the stack's real M3 components/tokens per the reference file — never approximate M3 with plain CSS when the stack has a real M3 library available (MUI, Material Web, Compose, Flutter all do).
5. Check responsiveness against the navigation rule above if the UI has navigation.

**Build-from-scratch task:**
1. Identify the stack (Section 1).
2. Clarify only what's essential (screen purpose, primary action) if not stated — don't interrogate; use sensible M3 defaults for everything else (Section 2's fallback seed, standard component variants) and say what you assumed.
3. Build directly with the stack's M3 components, using the type/shape/elevation tokens throughout, not just the color.

In both cases, when producing a runnable artifact (React component, HTML page), follow the project's normal artifact/file-creation rules — this skill governs *what to build*, not *where to put it*.

---

## Reference files

- `references/web-mui.md` — MUI v6 (`@mui/material`), theme setup for true M3 tokens (MUI's defaults are M2-ish; must configure `cssVariables`, `colorSchemes`, and the M3 typography/shape scale), component-by-component mapping.
- `references/web-html-css.md` — `@material/web` (Google's official Material Web Components, the most "authentic" M3 option for plain HTML) plus a hand-rolled CSS custom-properties fallback for when a build step isn't available.
- `references/flutter.md` — Flutter's built-in M3 support (`ThemeData(useMaterial3: true)`, `ColorScheme.fromSeed`), widget-by-widget mapping.
- `references/android-compose.md` — Jetpack Compose Material 3 (`androidx.compose.material3`), `MaterialTheme`, dynamic color (`dynamicColorScheme`) on Android 12+.
