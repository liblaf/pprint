# Custom Formatters

`liblaf.pprint` gives you four ways to customize formatting:

- Implement `__pretty__(self, ctx)` when you own the type.
- Use `register_type()` for one concrete class.
- Use `register_func()` for structural handlers that may or may not apply.
- Use `register_lazy()` when the target type lives in an optional dependency.

## Choose A Hook

Use the smallest hook that matches the problem:

- `__pretty__()` keeps the formatting logic next to the model you own.
- `register_type()` is the normal choice for a concrete third-party class.
- `register_func()` is useful when you need structural matching instead of type
  matching.
- `register_lazy()` keeps optional integrations cheap because it waits for the
  dependency to be imported elsewhere.

Builtin handlers already cover core containers, imported array libraries,
`fieldz`-compatible models, and `__rich_repr__`, so reach for a custom hook only
when the default behavior is not enough.

## Declarative Containers

For repr-like objects, the decorators keep a generator-based formatter small:

```python
from liblaf import pprint


class Point:
    def __init__(self, x: int, y: int = 0) -> None:
        self.x = x
        self.y = y

    @pprint.container()
    def __pretty__(self, ctx: pprint.Context):
        yield ctx.field("x", self.x)
        yield ctx.field("y", self.y, 0)
```

`@pprint.container()` uses `()` and does not impose an item limit.
`@pprint.list()` uses `[]` and `max_list`; `@pprint.dict()` uses `{}` and
`max_dict`. They accept `name`, `begin`, `end`, and `referable`. `ctx.item()`
uses its explicit index in reference paths, while `field()` hides a matching
default when `hide_defaults` is enabled.

## Resolution Order

The registry checks handlers in this order:

1. `obj.__pretty__(ctx)` when present
2. `register_type()` handlers, including subclass matches
3. `register_func()` handlers in reverse registration order
4. fallback repr-based formatting

Returning `None` from `__pretty__()` or `register_func()` lets the formatter
continue to the next option.

## A `__pretty__()` Method

If you control the class, `__pretty__(self, ctx)` keeps the formatting logic
next to the model:

```python
from rich.text import Text


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __pretty__(self, ctx):
        return ctx.container(
            obj=self,
            begin=Text("(", "repr.tag_start"),
            children=[ctx.name_value("x", self.x), ctx.name_value("y", self.y)],
            end=Text(")", "repr.tag_end"),
        )
```

The hook receives only `ctx`. Older `ctx, depth` examples are stale for this
package.

If `__pretty__()` returns `None`, the registry keeps looking for other
handlers.

## A Concrete Type

```python
from rich.text import Text

from liblaf.pprint import pformat, register_type


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


@register_type(Point)
def _pretty_point(obj: Point, ctx):
    return ctx.container(
        obj=obj,
        begin=Text("(", "repr.tag_start"),
        children=[ctx.name_value("x", obj.x), ctx.name_value("y", obj.y)],
        end=Text(")", "repr.tag_end"),
    )


print(pformat(Point(1, 2)), end="")
```

```text
Point(x=1, y=2)
```

`ctx.container()` prefixes the object's type name automatically for referable
objects, so `begin` and `end` usually only need delimiters.

`register_type()` uses `functools.singledispatch`, so subclasses also match
unless you register something more specific.

## Building Output With `PrettyContext`

`PrettyContext` exposes a few helpers that are enough for most handlers:

- `ctx.leaf(obj, text)` builds a scalar node from a `rich.text.Text` value.
- `ctx.positional(value)` wraps one positional child.
- `ctx.name_value(name, value)` builds `name=value` output.
- `ctx.key_value(key, value)` builds `key: value` output.
- `ctx.container(obj=..., begin=..., children=..., end=...)` builds repr-like
  tagged containers.

Use `Text` for `begin`, `end`, and custom leaf output. Those values flow
through the Rich rendering pipeline and are not plain strings.

`ctx.container()` is referable by default, which means repeated appearances
of the same object can later collapse into shared-reference tags. Use
`ctx.leaf(..., referable=False)` or `ctx.container(..., referable=False)`
for inline summaries that should always render as a value.

`ctx.name_value(name, value)` falls back to positional output when `name` is
falsey. That matches the built-in `__rich_repr__` adapter, where `("", value)`
and `(None, value)` are treated like positional items.

`ctx.container()` adds repr-style commas and spaces by default. Pass
`add_separators=False` when you want full control over child punctuation, or
`empty=...` when the empty rendering should not be just `begin + end`.

## Helper Utilities

`PrettyContext` also exposes a few utility helpers that are useful in custom
handlers:

- `ctx.truncate_list(items)` yields values up to `max_list`, then a truncation
  marker.
- `ctx.truncate_dict(items)` yields key-value pairs up to `max_dict`, then a
  truncation marker.
- `ctx.possibly_sorted(items)` sorts orderable values and preserves original
  order when sorting would fail.
- `ctx.add_separators(items)` attaches repr-style commas and spaces to existing
  wrapped items.

These helpers are how the built-in container handlers keep behavior aligned
with the public configuration surface.

## Structural Registration

`register_func()` is useful when the handler should inspect an object and decide
at runtime whether it applies. Return `None` to let the next handler try.
Functional handlers run after type-based handlers and are checked in reverse
registration order, so the most recently registered handler wins.

## Lazy Registration

`register_lazy(module, name)` defers registration until that module has already
been imported. It does not import the module for you. This is a good fit for
optional dependencies such as array or tensor types that should not be imported
just for pretty-printing.

`register("module.Type")` is equivalent decorator sugar when the target has a
stable import path.

```python
from rich.text import Text

from liblaf.pprint import register_lazy


@register_lazy("numpy", "ndarray")
def _pretty_ndarray(obj, ctx):
    return ctx.leaf(
        obj,
        Text(f"ndarray(shape={obj.shape!r}, dtype={obj.dtype!s})", "repr.tag_name"),
        referable=False,
    )
```

Once `numpy` is present in `sys.modules`, the handler is resolved and cached for
future formatting calls.

The built-in NumPy, JAX, Torch, and Warp formatters use the same pattern: they
stay dormant until the target package is imported elsewhere.

## When To Mark Things Referencable

Containers built with `ctx.container()` participate in shared-reference
tracking by default. That is usually what you want for mappings, sets,
frozensets, and object-like containers.

Use `referable=False` when a formatter is really just an inline summary.
Builtin scalar handlers and list-like sequence handlers use that path so they
always render their value instead of collapsing into `<Type @ path>` markers.
