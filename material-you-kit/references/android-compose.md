# Material 3 with Jetpack Compose (Android)

Use `androidx.compose.material3`, **not** `androidx.compose.material` (that's the M2 package — importing from the wrong package is the most common mistake here; double-check imports before anything else).

```kotlin
dependencies {
    implementation("androidx.compose.material3:material3:1.3.0") // check for latest
}
```

## Theme setup

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true, // Android 12+ wallpaper-based color, M3's signature feature
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme(primary = Color(0xFFD0BCFF), /* ... */)
        else -> lightColorScheme(primary = Color(0xFF6750A4), /* ... */)
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(), // M3 default type scale; override per-style if needed
        shapes = Shapes(), // M3 default shape scale
        content = content
    )
}
```

If not using dynamic color, generate the full scheme from one seed with Google's `material-color-utilities` library (`Hct`, `SchemeContent`/`SchemeTonalSpot`) rather than picking each role by hand — same tool family used for the web stacks, ensures cross-platform consistency if the user also has a web app.

## Component mapping

| M3 concept | Compose composable |
|---|---|
| Filled button | `Button` |
| Filled tonal button | `FilledTonalButton` |
| Elevated button | `ElevatedButton` |
| Outlined button | `OutlinedButton` |
| Text button | `TextButton` |
| FAB (regular/small/large) | `FloatingActionButton` (size via `Modifier.size`) / `SmallFloatingActionButton` / `LargeFloatingActionButton` |
| Extended FAB | `ExtendedFloatingActionButton` |
| Icon button | `IconButton` |
| Segmented button | `SingleChoiceSegmentedButtonRow` / `MultiChoiceSegmentedButtonRow` + `SegmentedButton` |
| Card (elevated/filled/outlined) | `ElevatedCard` / `Card` / `OutlinedCard` |
| Text field | `TextField` (filled) / `OutlinedTextField` |
| Chip (assist/filter/input/suggestion) | `AssistChip` / `FilterChip` / `InputChip` / `SuggestionChip` |
| Top app bar | `TopAppBar` / `CenterAlignedTopAppBar` / `MediumTopAppBar` / `LargeTopAppBar` |
| Navigation bar (mobile) | `NavigationBar` + `NavigationBarItem` |
| Navigation rail | `NavigationRail` + `NavigationRailItem` |
| Navigation drawer | `ModalNavigationDrawer` / `PermanentNavigationDrawer` |
| Dialog | `AlertDialog` |
| Snackbar | `Snackbar` via `SnackbarHost` |
| Switch | `Switch` |
| Slider | `Slider` |
| Tabs | `TabRow` + `Tab` |
| Menu | `DropdownMenu` |
| Divider | `HorizontalDivider` / `VerticalDivider` |
| Badge | `Badge` |
| Progress | `CircularProgressIndicator` / `LinearProgressIndicator` |
| Bottom sheet | `ModalBottomSheet` |
| Date/time picker | `DatePicker` / `TimePicker` |

## Adaptive layout (window size classes)

Use `androidx.compose.material3.windowsizeclass` (`calculateWindowSizeClass`) to branch `NavigationBar` (Compact) → `NavigationRail` (Medium) → `PermanentNavigationDrawer` (Expanded) — the same three-tier pattern as the other stacks, so a cross-platform product stays consistent.

## Common mistakes to avoid
- Importing from `androidx.compose.material.*` instead of `androidx.compose.material3.*` — they coexist in some projects and only one is M3.
- Forgetting `dynamicColor` guard for API < 31 — dynamic color APIs crash below Android 12 without the `Build.VERSION.SDK_INT` check shown above.
