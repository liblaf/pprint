# PPrint

`liblaf.pprint` presents Python values for terminals, logs, and snapshots. It
replaces familiar pretty-printing workflows with a capability-led interface,
not a drop-in copy of another library's functions.

## One presentation, three destinations

`pretty()` constructs a `Pretty` object once. Pass it to Rich when the target
console should choose line breaks; use `.text()` for a deterministic snapshot;
or use `.show()` for immediate terminal output.

```python
from rich.console import Console

from liblaf.pprint import pretty

presentation = pretty({"alpha": [1, 2, 3]})

assert presentation.text() == "{'alpha': [1, 2, 3]}"
Console(width=12).print(presentation)
presentation.show()
```

`Pretty.text(width=88)` returns text without a trailing newline. Its fixed,
markup-safe console makes snapshots reproducible. `Pretty.show()` writes to a
provided Rich console or the active global one, and emits exactly one final
newline. Rich rendering remains width-aware because `Pretty` implements
`__rich_console__`.

## Formatting options

`pretty()` and `format_frame_variables()` accept the same keyword overrides:

| Keyword | Default | Meaning |
| --- | --- | --- |
| `max_level` | `6` | Maximum nesting depth before children collapse to `...`. |
| `max_list` | `6` | Maximum visible items in list-like containers. |
| `max_array` | `5` | Maximum array items forwarded to repr-style handlers. |
| `max_dict` | `4` | Maximum visible key-value pairs in mappings. |
| `max_string` | `30` | Maximum string repr length before truncation. |
| `max_long` | `40` | Maximum integer repr length before truncation. |
| `max_other` | `30` | Maximum repr length for other scalar values. |
| `indent` | `"|   "` | Indentation used when layouts break across lines. |
| `hide_defaults` | `True` | Hide default-valued `fieldz` and `__rich_repr__` fields. |

Each value can also come from a `PPRINT_*` environment variable. For example,
`PPRINT_MAX_LIST=1` has the same effect as `pretty(obj, max_list=1)`.

`indent` accepts plain text, Rich markup, ANSI-colored text, or
`rich.text.Text`.

## Built in

`liblaf.pprint` handles scalar values, `dict`, `list`, `tuple`, `set`, and
`frozenset` without registration. It recognizes `fieldz`-compatible models,
objects with `__rich_repr__`, and imported NumPy, JAX, Torch, and Warp arrays.
Optional array integrations stay lazy: no optional framework is imported merely
to format an ordinary Python value.

```python
import attrs

from liblaf.pprint import pretty


@attrs.define
class Point:
    x: int = 1
    y: int = 2


assert pretty(Point()).text() == "Point()"
assert pretty(Point(), hide_defaults=False).text() == "Point(x=1, y=2)"
```

Arrays whose every dimension is shorter than `max_array` retain their normal
repr; larger arrays use a compact dtype, shape, framework, and, when exposed,
device summary.

## Reference tracking

Referable objects are annotated at their first and shallowest appearance, then
replaced by a path reference later. Cycles stay readable without losing object
identity. If an anchor path exceeds `max_other`, the tag falls back to a compact
hexadecimal identity.

```python
from liblaf.pprint import pretty

child = {"x": 1}
print(pretty({"left": child, "right": child}).text())
```

```text
{
|   'left': {'x': 1},  # <dict @ $['left']>
|   'right': <dict @ $['left']>
}
```

## Custom formatting

Implement `__pretty__(self, ctx)` when you own a type. Use `register()` or
`register_type()` for concrete classes, `register_func()` for structural
matching, and `register_lazy()` for optional dependencies. `PrettyContext`
provides builders for containers, leaves, positional items, name-value items,
and key-value items. The `container`, `list`, and `dict` decorators add the
ordinary repr-like punctuation and respect their configured limits.

See [Custom Formatters](guides/custom-formatters.md) for examples.

## Frame-variable batches

`format_frame_variables()` is a narrow integration seam for traceback-style
renderers. It accepts ordered local-variable mappings, traces references across
the complete batch, and returns one tuple of `name = value` strings per frame.
The caller retains filenames, source excerpts, headings, and final output.

```python
from liblaf.pprint import format_frame_variables

shared = {"answer": 42}
frames = format_frame_variables(({"payload": shared}, {"again": shared}))

assert frames[1] == ("again = <dict @ $frames[0].payload>",)
```

## Internal pipeline

`Pretty` owns the wrapped, traced, and lowered pipeline internally. The
individual stages remain implementation details rather than a root-level
extension surface. Custom formatters should use `PrettyContext` instead.

See the [API reference](reference/liblaf/pprint/README.md) for signatures and
source-backed docstrings.
