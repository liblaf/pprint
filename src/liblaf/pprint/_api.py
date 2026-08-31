"""Top-level formatting helpers.

These functions are the public entry point into the wrapped, traced, and
lowered pipeline that powers `liblaf.pprint`. Use [`pformat`][liblaf.pprint.pformat]
for captured plain text, [`render`][liblaf.pprint.render] for a Rich renderable,
and [`pprint`][liblaf.pprint.pprint] for console output.
"""

from collections.abc import Iterable, Mapping
from typing import Any, Unpack

import rich
from rich.console import Console, RenderableType
from rich.text import Text

from liblaf.pprint.custom import PrettyContext
from liblaf.pprint.stages.lowered import LoweredNode
from liblaf.pprint.stages.traced import (
    LowerContext,
    TracedContainer,
    TracedNameValueItem,
    TracedNode,
    TracedPositionalItem,
)
from liblaf.pprint.stages.wrapped import WrappedNode, WrappedPositionalItem

from ._config import PrettyOptions, PrettyOverrides, config


def pformat(obj: Any, **kwargs: Unpack[PrettyOverrides]) -> str:
    """Format `obj` as plain text.

    This helper lowers the object and captures the Rich renderable with a safe
    default console. Use [`render`][liblaf.pprint.render] when the final layout
    should depend on a specific Rich console width.

    Args:
        obj: Object to format.
        **kwargs: Per-call overrides merged with [`config`][liblaf.pprint.config].

    Returns:
        Plain-text repr-like output.

    Examples:
        >>> pformat({"answer": [1, 2]})
        "{'answer': [1, 2]}"
    """
    lowered: LoweredNode = _lower(obj, **kwargs)
    return lowered.to_plain()


def render(obj: Any, **kwargs: Unpack[PrettyOverrides]) -> RenderableType:
    """Build a Rich renderable for `obj`.

    The returned lowered node chooses between flat and broken layouts when Rich
    renders it through a `Console`.

    Args:
        obj: Object to format.
        **kwargs: Per-call overrides merged with [`config`][liblaf.pprint.config].

    Returns:
        A width-aware Rich renderable.
    """
    return _lower(obj, **kwargs)


def _lower(obj: Any, **kwargs: Unpack[PrettyOverrides]) -> LoweredNode:
    """Run the internal wrapped-to-lowered pipeline for one object."""
    options: PrettyOptions = PrettyOptions(**{**config.to_dict(), **kwargs})
    pretty_ctx: PrettyContext = PrettyContext(options=options)
    wrapped: WrappedNode = pretty_ctx.wrap_lazy(obj)
    traced: TracedNode = pretty_ctx.trace(wrapped)
    lower_ctx: LowerContext = pretty_ctx.finish()
    lowered: LoweredNode = traced.lower(lower_ctx)
    return lowered


def pformat_frames(
    frames: Iterable[Mapping[str, Any]], **kwargs: Unpack[PrettyOverrides]
) -> tuple[tuple[str, ...], ...]:
    """Format local-variable mappings from several frames in one pass.

    Each returned inner tuple contains the ``name = value`` lines for one input
    frame. The function deliberately does not add filenames, source excerpts, or
    frame headings: callers such as traceback renderers own that presentation.
    Shared values are nevertheless traced across every supplied frame. Their
    tags use ``$frames[frame-index].variable`` paths.

    Args:
        frames: Frame-local mappings in traceback order. Mapping iteration order
            becomes variable display order.
        **kwargs: Per-call overrides merged with [`config`][liblaf.pprint.config].

    Returns:
        Plain variable lines grouped by input frame.

    Examples:
        >>> shared = {"answer": 42}
        >>> lines = pformat_frames(({"payload": shared}, {"again": shared}))
        >>> lines[1]
        ('again = <dict @ $frames[0].payload>',)
    """
    options: PrettyOptions = PrettyOptions(**{**config.to_dict(), **kwargs})
    pretty_ctx: PrettyContext = PrettyContext(options=options)
    wrapped_frames: list[WrappedPositionalItem] = []
    for index, variables in enumerate(frames):
        children = [
            pretty_ctx.name_value(name, value, sep=Text(" = ", "repr.attrib_equal"))
            for name, value in variables.items()
        ]
        frame = pretty_ctx.container(
            object(),
            Text(),
            children,
            Text(),
            add_separators=False,
            name=Text(),
            referable=False,
        )
        item = WrappedPositionalItem(value=frame)
        item.path_segment = f"[{index}]"
        wrapped_frames.append(item)
    root = pretty_ctx.container(
        object(),
        Text(),
        wrapped_frames,
        Text(),
        add_separators=False,
        name=Text(),
        referable=False,
    )
    traced_root: TracedNode = pretty_ctx.trace(root, path="$frames")
    assert isinstance(traced_root, TracedContainer)
    lower_ctx: LowerContext = pretty_ctx.finish()
    formatted: list[tuple[str, ...]] = []
    for frame in traced_root.children:
        assert isinstance(frame, TracedPositionalItem)
        assert isinstance(frame.value, TracedContainer)
        lines: list[str] = []
        for variable in frame.value.children:
            assert isinstance(variable, TracedNameValueItem)
            lines.append(variable.lower(lower_ctx).to_plain().rstrip("\n"))
        formatted.append(tuple(lines))
    return tuple(formatted)


def plower(obj: Any, **kwargs: Unpack[PrettyOverrides]) -> LoweredNode:
    """Build the concrete lowered node used by [`render`][liblaf.pprint.render].

    This advanced compatibility interface exposes the current final stage. New
    callers should depend on `render()`, whose interface promises only Rich's
    renderable protocol rather than a pipeline implementation type.
    """
    return _lower(obj, **kwargs)


def pprint(
    obj: Any, *, console: Console | None = None, **kwargs: Unpack[PrettyOverrides]
) -> None:
    """Format `obj` and print it through a Rich console.

    This is the side-effecting companion to [`render`][liblaf.pprint.render].

    Args:
        obj: Object to format.
        console: Console to render into. When omitted, the active global Rich console
            is used.
        **kwargs: Per-call overrides merged with [`config`][liblaf.pprint.config].
    """
    if console is None:
        console: Console = rich.get_console()
    console.print(render(obj, **kwargs))
    # Lowered renderables yield their own segments, so Rich's `end` argument
    # cannot add a newline after them. An empty print owns that final line.
    console.print()


pp = pprint
