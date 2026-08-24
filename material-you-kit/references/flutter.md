# Material 3 with Flutter

Flutter ships M3 widgets, but **M3 is opt-in** — a Flutter app not explicitly configured for it renders Material 2 (rounded-but-wrong shapes, old FAB shape, uppercase buttons). Always set this explicitly:

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true, // required — do not skip
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF6750A4), // brand color or sensible default
      brightness: Brightness.light,
    ),
  ),
  darkTheme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF6750A4),
      brightness: Brightness.dark,
    ),
  ),
  themeMode: ThemeMode.system,
  home: const HomeScreen(),
)
```

`ColorScheme.fromSeed` generates the full M3 role set (primary, primaryContainer, onPrimaryContainer, surface, surfaceContainerLow/High, outline, etc.) automatically — this is the easiest path to a correct token set of any stack. Access roles via `Theme.of(context).colorScheme.primary`, never hardcode a `Color(0x...)` inline in a widget.

On Android 12+, you can use the device wallpaper's dynamic color instead of a fixed seed via the `dynamic_color` package:

```dart
DynamicColorBuilder(
  builder: (lightScheme, darkScheme) => MaterialApp(
    theme: ThemeData(useMaterial3: true, colorScheme: lightScheme ?? fallbackLight),
    darkTheme: ThemeData(useMaterial3: true, colorScheme: darkScheme ?? fallbackDark),
    ...
  ),
)
```

## Component mapping

| M3 concept | Flutter widget |
|---|---|
| Filled button | `FilledButton` |
| Filled tonal button | `FilledButton.tonal` |
| Elevated button | `ElevatedButton` |
| Outlined button | `OutlinedButton` |
| Text button | `TextButton` |
| FAB (regular/small/large) | `FloatingActionButton` / `FloatingActionButton.small` / `FloatingActionButton.large` |
| Extended FAB | `FloatingActionButton.extended` |
| Icon button | `IconButton` |
| Segmented button | `SegmentedButton<T>` |
| Card (elevated/filled/outlined) | `Card` with `elevation`/`color` set, or `Card.filled` / `Card.outlined` |
| Text field | `TextField` with `InputDecoration(filled: true)` or `border: OutlineInputBorder()` |
| Chip (assist/filter/input/suggestion) | `ActionChip` / `FilterChip` / `InputChip` / `ChoiceChip` |
| Top app bar | `AppBar` (M3 style is default once `useMaterial3: true`) |
| Navigation bar (mobile) | `NavigationBar` (replaces old `BottomNavigationBar`) |
| Navigation rail | `NavigationRail` |
| Navigation drawer | `NavigationDrawer` |
| Dialog | `AlertDialog` or `Dialog.fullscreen` |
| Snackbar | `SnackBar` via `ScaffoldMessenger` |
| Switch | `Switch` |
| Slider | `Slider` |
| Tabs | `TabBar` + `TabBarView` |
| Menu | `MenuAnchor` or `DropdownMenu` |
| Divider | `Divider` |
| Badge | `Badge` |
| Progress | `CircularProgressIndicator` / `LinearProgressIndicator` |
| Bottom sheet | `showModalBottomSheet` |
| Date/time picker | `showDatePicker` / `showTimePicker` (M3 style automatic under `useMaterial3`) |

## Responsive navigation (Flutter-specific pattern)

Use `LayoutBuilder` or a package like `flutter_adaptive_scaffold` to switch `NavigationBar` → `NavigationRail` → `NavigationDrawer` at standard M3 breakpoints (compact <600dp, medium 600-839dp, expanded ≥840dp) rather than shipping one nav pattern at all sizes.

## Common mistake to avoid
Forgetting `useMaterial3: true` on **both** `theme` and `darkTheme` — setting it on only one produces an inconsistent app between light/dark mode.
