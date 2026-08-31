"""Layout strategy interfaces used by lowered nodes and items."""

import abc
from collections.abc import Iterable

import attrs
from rich.console import RenderResult

from ._context import CompileContext


@attrs.frozen
class Layout(abc.ABC):
    """Candidate rendering strategy for a lowered node or item."""

    @abc.abstractmethod
    def fits(self, ctx: CompileContext) -> bool: ...

    @abc.abstractmethod
    def render(self, ctx: CompileContext) -> RenderResult: ...

    @abc.abstractmethod
    def supports(self, ctx: CompileContext) -> bool: ...


def choose_layout(layouts: Iterable[Layout], ctx: CompileContext) -> Layout:
    """Pick the first supported layout that fits, or the last fallback."""
    for layout in layouts:
        if not layout.supports(ctx):
            continue
        if layout.fits(ctx):
            return layout
        fallback: Layout = layout
    return fallback
