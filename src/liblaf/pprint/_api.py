"""Capability-led public presentations for Python values.

[`pretty`][liblaf.pprint.pretty] constructs a [`Pretty`][liblaf.pprint.Pretty]
presentation. The presentation can be handed to Rich, captured as deterministic
plain text, or shown immediately.
"""

from collections.abc import Iterable, Mapping
from typing import Any, Unpack

import attrs
import rich
from rich.console import Console, ConsoleOptions, RenderResult
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


@attrs.frozen
class Pretty:
    """A reusable, Rich-capable presentation of one Python value.

    `Pretty` is the stable public presentation boundary. It keeps the lowered
    pipeline node private while exposing three deliberate capabilities:
    pass it to a Rich console, call [`text`][liblaf.pprint.Pretty.text] for a
    deterministic plain-text snapshot, or call
    [`show`][liblaf.pprint.Pretty.show] for terminal output.
    """

    _lowered: LoweredNode = attrs.field(repr=False)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render through Rich with line breaking chosen by `console`."""
        yield from self._lowered.__rich_console__(console, options)

    def text(self, *, width: int = 88) -> str:
        """Return a deterministic plain-text snapshot.

        Args:
            width: Target terminal width used to choose flat or broken layouts.

        Returns:
            The presentation without a trailing newline.

        Raises:
            AssertionError: If `width` is not positive.
        """
        assert width > 0
        console = Console(
            color_system=None,
            soft_wrap=True,
            width=width,
            no_color=True,
            markup=False,
            emoji=False,
            highlight=False,
        )
        return self._lowered.to_plain(console=console).rstrip("\n")

    def show(self, *, console: Console | None = None) -> None:
        """Write this presentation to `console` with exactly one final newline."""
        if console is None:
            console = rich.get_console()
        console.print(self)
        # Lowered renderables own their segments, so Rich cannot append `end`
        # to their final segment. This empty print owns the one final newline.
        console.print()


def pretty(value: Any, **overrides: Unpack[PrettyOverrides]) -> Pretty:
    """Construct a Rich-capable presentation of `value`.

    Args:
        value: Python value to present.
        **overrides: Per-call overrides merged with
            [`config`][liblaf.pprint.config].

    Returns:
        A presentation that can be rendered by Rich, captured with `.text()`,
        or emitted with `.show()`.

    Examples:
        >>> pretty({"answer": [1, 2]}).text()
        "{'answer': [1, 2]}"
    """
    return Pretty(_lower(value, **overrides))


def _lower(value: Any, **overrides: Unpack[PrettyOverrides]) -> LoweredNode:
    """Run the internal wrapped-to-lowered pipeline for one value."""
    options = PrettyOptions(**{**config.to_dict(), **overrides})
    pretty_ctx = PrettyContext(options=options)
    wrapped: WrappedNode = pretty_ctx.wrap_lazy(value)
    traced: TracedNode = pretty_ctx.trace(wrapped)
    lower_ctx: LowerContext = pretty_ctx.finish()
    return traced.lower(lower_ctx)


def format_frame_variables(
    frames: Iterable[Mapping[str, Any]], **overrides: Unpack[PrettyOverrides]
) -> tuple[tuple[str, ...], ...]:
    """Format frame-local variable mappings with one shared reference graph.

    Each returned inner tuple contains the ``name = value`` lines for one input
    frame. The caller owns filenames, source excerpts, frame headings, and the
    final traceback presentation. Shared values are traced across every
    supplied frame; tags use ``$frames[frame-index].variable`` paths.

    Args:
        frames: Frame-local mappings in traceback order. Mapping iteration order
            becomes variable display order.
        **overrides: Per-call overrides merged with
            [`config`][liblaf.pprint.config].

    Returns:
        Plain variable lines grouped by input frame.
    """
    options = PrettyOptions(**{**config.to_dict(), **overrides})
    pretty_ctx = PrettyContext(options=options)
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
