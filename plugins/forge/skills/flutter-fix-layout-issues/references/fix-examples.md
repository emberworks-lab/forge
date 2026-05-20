# Fix examples — input/output code pairs

Three canonical fixes for the three most common layout exceptions.

## 1. Unbounded height — ListView in Column

Throws: `Vertical viewport was given unbounded height`.

```dart
// Before
Column(
  children: <Widget>[
    const Text('Header'),
    ListView(
      children: const <Widget>[
        ListTile(title: Text('Item 1')),
        ListTile(title: Text('Item 2')),
      ],
    ),
  ],
)

// After — Expanded constrains ListView to remaining Column space
Column(
  children: <Widget>[
    const Text('Header'),
    Expanded(
      child: ListView(
        children: const <Widget>[
          ListTile(title: Text('Item 1')),
          ListTile(title: Text('Item 2')),
        ],
      ),
    ),
  ],
)
```

## 2. Unbounded width — TextField in Row

Throws: `An InputDecorator…cannot have an unbounded width`.

```dart
// Before
Row(
  children: [
    const Icon(Icons.search),
    TextField(),
  ],
)

// After — Expanded gives TextField the remaining Row width
Row(
  children: [
    const Icon(Icons.search),
    Expanded(
      child: TextField(),
    ),
  ],
)
```

## 3. RenderFlex overflow — long text in Row

Throws: `A RenderFlex overflowed by X pixels on the right`.

```dart
// Before
Row(
  children: [
    const Icon(Icons.info),
    const Text(
      'This is a very long text string that will definitely overflow the available screen width and cause a RenderFlex error.',
    ),
  ],
)

// After — Expanded forces the Text to wrap within available constraints
Row(
  children: [
    const Icon(Icons.info),
    Expanded(
      child: Text(
        'This is a very long text string that will definitely overflow the available screen width and cause a RenderFlex error.',
      ),
    ),
  ],
)
```

## Verification

After each fix, hot-reload (`r` in `flutter run`, or the Flutter MCP `hot_reload` tool). The red error screen / yellow-black stripes should disappear. If a new layout exception surfaces, treat it as a new diagnostic and re-enter the workflow.
