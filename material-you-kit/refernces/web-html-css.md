# Material 3 with plain HTML/CSS (no React)

Two options, in order of preference:

## Option A (preferred): `@material/web` — Google's official Material Web Components

Real M3 components as framework-agnostic custom elements. Use this whenever a build step (or even just an ES module `<script type="module">` import from a CDN) is acceptable.

```html
<script type="importmap">
{
  "imports": {
    "@material/web/": "https://esm.run/@material/web/"
  }
}
</script>
<script type="module">
  import '@material/web/button/filled-button.js';
  import '@material/web/button/outlined-button.js';
  import '@material/web/textfield/outlined-text-field.js';
  import '@material/web/card/elevated-card.js'; // note: check current package for card, some layouts hand-roll cards with tokens
  import '@material/web/all.js'; // or import everything if bundle size isn't a concern for a demo/artifact
</script>

<md-filled-button>Save</md-filled-button>
<md-outlined-button>Cancel</md-outlined-button>
<md-outlined-text-field label="Email"></md-outlined-text-field>
```

Theme via CSS custom properties (Material Web reads these directly — this **is** the token system, not an approximation):

```css
:root {
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  --md-sys-color-on-primary-container: #21005D;
  --md-sys-color-secondary: #625B71;
  --md-sys-color-surface: #FFFBFE;
  --md-sys-color-surface-container: #F3EDF7;
  --md-sys-color-surface-container-high: #ECE6F0;
  --md-sys-color-on-surface: #1C1B1F;
  --md-sys-color-outline: #79747E;
  --md-sys-shape-corner-medium: 12px;
  --md-sys-typescale-body-large-font: 'Roboto', sans-serif;
  --md-sys-typescale-body-large-size: 16px;
}
```

To derive a full role set from one seed color rather than hand-picking every variable, use `@material/material-color-utilities` (same package MUI setups use) via a small script, or Google's Material Theme Builder (material-foundation.github.io/material-theme-builder) to export the token set once and paste it in.

## Option B: hand-rolled CSS tokens (no build step at all, single static file)

Use this only when a `<script type="module">` CDN import genuinely isn't viable (e.g. must work with `file://`, or extremely restrictive environment). You are reimplementing M3 by hand — be disciplined about tokens so it doesn't drift into "rounded Bootstrap."

```css
:root {
  /* Color roles — same values as Option A */
  --primary: #6750A4; --on-primary: #fff;
  --primary-container: #EADDFF; --on-primary-container: #21005D;
  --surface: #FFFBFE; --on-surface: #1C1B1F;
  --surface-container-low: #F7F2FA;
  --surface-container: #F3EDF7;
  --surface-container-high: #ECE6F0;
  --outline: #79747E; --outline-variant: #CAC4D0;

  /* Shape scale */
  --shape-xs: 4px; --shape-sm: 8px; --shape-md: 12px; --shape-lg: 16px; --shape-xl: 28px; --shape-full: 999px;

  /* Elevation (shadow approximations of M3 levels 0-5) */
  --elevation-1: 0 1px 2px 0 rgba(0,0,0,0.30), 0 1px 3px 1px rgba(0,0,0,0.15);
  --elevation-2: 0 1px 2px 0 rgba(0,0,0,0.30), 0 2px 6px 2px rgba(0,0,0,0.15);
  --elevation-3: 0 1px 3px 0 rgba(0,0,0,0.30), 0 4px 8px 3px rgba(0,0,0,0.15);
}

.md-button--filled {
  background: var(--primary); color: var(--on-primary);
  border-radius: var(--shape-full); padding: 10px 24px;
  font: 500 14px/20px 'Roboto', sans-serif; border: none; cursor: pointer;
  transition: box-shadow .15s;
}
.md-button--filled:hover { box-shadow: var(--elevation-1); }

.md-card {
  background: var(--surface-container-low);
  border-radius: var(--shape-md);
  box-shadow: var(--elevation-1);
  padding: 16px;
}

.md-textfield--outlined {
  border: 1px solid var(--outline);
  border-radius: var(--shape-xs);
  padding: 16px; color: var(--on-surface); background: transparent;
}
.md-textfield--outlined:focus { border: 2px solid var(--primary); outline: none; }
```

State layers (hover/pressed) in hand-rolled CSS: overlay the content color at fixed opacity rather than swapping to a flat "hover color":

```css
.md-button--filled { position: relative; overflow: hidden; }
.md-button--filled::after {
  content: ''; position: absolute; inset: 0; background: var(--on-primary);
  opacity: 0; transition: opacity .15s; pointer-events: none;
}
.md-button--filled:hover::after { opacity: 0.08; }
.md-button--filled:active::after { opacity: 0.12; }
```

## Component checklist (both options)
Buttons (filled/outlined/text/tonal), FAB, cards (elevated/filled/outlined), text fields (filled/outlined), chips, top app bar, navigation (bar → rail → drawer by breakpoint), dialog, snackbar, switch, checkbox, radio, slider, tabs, menu, divider, badge, progress indicator. See the component table in the main SKILL.md for which M3 variant fits which use case.
