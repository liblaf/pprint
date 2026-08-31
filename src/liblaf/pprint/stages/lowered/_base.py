"""Base Rich renderables used by the final lowering stage."""

import abc
from collections.abc import Iterable
from typing import Any

import attrs
from rich.console import Console, ConsoleOptions, RenderResult

from ._context import CompileContext
from ._layout import Layout, choose_layout


@attrs.frozen
class Lowered(abc.ABC):
    """Abstract Rich renderable produced by the lowering stage.

    Subclasses expose one or more layout candidates through
    [`layouts()`][liblaf.pprint.stages.lowered.Lowered.layouts]. Rich calls
    [`__rich_console__`][liblaf.pprint.stages.lowered.Lowered.__rich_console__]
    later, so line wrapping still depends on the target console width.
    """

    def __str__(self) -> str:
        return self.to_plain()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        ctx: CompileContext = CompileContext(console, options)
        return self.render(ctx)

    @abc.abstractmethod
    def layouts(self) -> Iterable[Layout]: ...

    def render(self, ctx: CompileContext) -> RenderResult:
        layout: Layout = choose_layout(self.layouts(), ctx)
        return layout.render(ctx)

    def to_plain(self, console: Console | None = None, **kwargs: Any) -> str:
        """Render this value into plain text.

        Args:
            console: Optional Rich console to render into. When omitted,
                `liblaf.pprint` creates a markup-safe console with soft wrapping
                enabled.
            **kwargs: Extra keyword arguments forwarded to
                [`Console.print`][rich.console.Console.print].

        Returns:
            The captured plain-text rendering.
        """
        if console is None:
            console: Console = Console(
                color_system=None,
                soft_wrap=True,
                width=88,
                no_color=True,
                markup=False,
                emoji=False,
                highlight=False,
            )
        kwargs.setdefault("soft_wrap", True)
        with console.capture() as capture:
            console.print(self, **kwargs)
        return capture.get()
