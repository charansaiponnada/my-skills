# Material 3 with React + MUI v6

MUI's **default** theme is closer to Material 2. To get real M3, you must explicitly configure the theme — don't just import components and assume you're done.

## Theme setup (do this first, always)

```jsx
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  cssVariables: true, // enables CSS var-based theming, closer to M3's token model
  colorSchemes: {
    light: {
      palette: {
        primary: { main: '#6750A4' },      // seed — swap for brand/derived color
        secondary: { main: '#625B71' },
        tertiary: { main: '#7D5260' },
        error: { main: '#B3261E' },
        background: { default: '#FFFBFE', paper: '#F7F2FA' }, // surface / surface-container
      },
    },
    dark: {
      palette: {
        primary: { main: '#D0BCFF' },
        secondary: { main: '#CCC2DC' },
        tertiary: { main: '#EFB8C8' },
        background: { default: '#1C1B1F', paper: '#211F26' },
      },
    },
  },
  shape: { borderRadius: 12 }, // M3 "medium" default; override per-component below
  typography: {
    // Map MUI's variant names to M3 type-scale sizes (px, M3 spec)
    h1: { fontSize: 57, fontWeight: 400 }, // Display Large
    h2: { fontSize: 45, fontWeight: 400 }, // Display Medium
    h3: { fontSize: 36, fontWeight: 400 }, // Display Small
    h4: { fontSize: 32, fontWeight: 400 }, // Headline Large
    h5: { fontSize: 28, fontWeight: 400 }, // Headline Medium
    h6: { fontSize: 24, fontWeight: 400 }, // Headline Small
    subtitle1: { fontSize: 22, fontWeight: 500 }, // Title Large
    subtitle2: { fontSize: 16, fontWeight: 500 }, // Title Medium
    body1: { fontSize: 16, fontWeight: 400 }, // Body Large
    body2: { fontSize: 14, fontWeight: 400 }, // Body Medium
    button: { fontSize: 14, fontWeight: 500, textTransform: 'none' }, // Label Large — M3 buttons are NOT uppercase
  },
});

export default function App({ children }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
```

If seeding from a single brand color rather than hand-picking all roles, generate the tonal palette with Google's own tool logic — use the `@material/material-color-utilities` package (`argbFromHex`, `themeFromSourceColor`) rather than guessing tints by eye.

## Component mapping

| M3 concept | MUI component / prop |
|---|---|
| Filled button | `<Button variant="contained">` |
| Elevated button | `<Button variant="contained" disableElevation={false}>` on a `surface`-colored background (MUI doesn't have a distinct "elevated" variant — style contained button with surface bg + shadow) |
| Filled tonal button | `<Button variant="contained" color="secondary">` using the `*-container` color, or custom `sx` with `secondaryContainer` |
| Outlined button | `<Button variant="outlined">` |
| Text button | `<Button variant="text">` |
| FAB (regular/small/large) | `<Fab size="medium"/"small"/"large">` |
| Extended FAB | `<Fab variant="extended">` |
| Icon button | `<IconButton>` |
| Segmented button | `<ToggleButtonGroup exclusive>` + `<ToggleButton>` |
| Card (elevated) | `<Card elevation={1}>` (default) |
| Card (filled) | `<Card variant="outlined" sx={{ borderColor: 'transparent', bgcolor: 'surfaceContainerHighest' }}>` |
| Card (outlined) | `<Card variant="outlined">` |
| Text field (filled) | `<TextField variant="filled">` |
| Text field (outlined) | `<TextField variant="outlined">` (M3 default preference) |
| Chip (assist/filter/input/suggestion) | `<Chip>` — variant behavior via `variant="filled"/"outlined"` + `onDelete`/`icon` props |
| Top app bar | `<AppBar position="static" elevation={0}>` + `<Toolbar>` |
| Navigation bar (mobile) | `<BottomNavigation>` + `<BottomNavigationAction>` |
| Navigation rail | `<Drawer variant="permanent" sx={{ width: 80 }}>` with icon-only items (MUI has no native rail — compose from Drawer) |
| Navigation drawer | `<Drawer variant="permanent"/"persistent">` |
| Dialog | `<Dialog>` |
| Snackbar | `<Snackbar>` |
| Switch | `<Switch>` |
| Slider | `<Slider>` |
| Tabs | `<Tabs>` + `<Tab>` |
| Menu | `<Menu>` + `<MenuItem>` |
| Divider | `<Divider>` |
| Badge | `<Badge>` |
| Progress | `<CircularProgress>` / `<LinearProgress>` |

## Shape tokens per component (MUI `sx` or theme `components` override)

- Buttons / chips: `full` (pill) — MUI buttons default to this already via `borderRadius: 9999` in most M3 themes.
- Cards: `medium` (12px).
- Dialogs: `extra-large` (28px).
- Text fields: `extra-small` top corners only for filled variant (4px), `extra-small` all corners for outlined.
- FAB: `large` (16px) for regular, `full` for small.

Set these via `theme.components.MuiCard.styleOverrides.root`, etc., rather than one-off `sx` on every instance, so it's consistent across the app.

## Common mistake to avoid
Don't leave MUI's default uppercase button text (`textTransform: 'uppercase'` is an M2 holdover) — M3 buttons are sentence case. Already handled above via `typography.button.textTransform: 'none'`.
