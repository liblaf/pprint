"""Lowered positional item layouts."""

import functools
from collections.abc import Generator
from typing import Self, override

import attrs
from rich.console import RenderResult
from rich.text import Text

from liblaf.pprint.literals import COMMENT_GAP, EMPTY

from ._context import CompileContext
from ._item_base import LoweredItem
from ._layout import Layout
from ._node_base import LoweredNode
from ._node_leaf import LoweredLeaf


@attrs.frozen
class LoweredPositionalItem(LoweredItem):
    """Lowered positional item used for container children and ellipses."""

    value: LoweredNode

    @classmethod
    def ellipsis(cls, *, prefix: Text = EMPTY, suffix: Text = EMPTY) -> Self:
        return cls(LoweredLeaf.ellipsis(), prefix=prefix, suffix=suffix)

    @override
    def layouts(self) -> Generator[Layout]:
        yield Inline(self)
        yield Flat(self)
        yield Break(self)

    @functools.cached_property
    @override
    def width_inline(self) -> int | None:
        if self.value.annotation or self.value.width_flat is None:
            return None
        return self.prefix.cell_len + self.value.width_flat + self.suffix.cell_len


@attrs.frozen
class Inline(Layout):
    item: LoweredPositionalItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.value.width_flat is not None
        return (
            self.item.prefix.cell_len
            + self.item.value.width_flat
            + self.item.suffix.cell_len
            <= ctx.remaining_width
        )

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.render(self.item.prefix)
        yield from self.item.value.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.suffix)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return ctx.column > 0 and self.item.value.width_flat is not None


@attrs.frozen
class Flat(Layout):
    item: LoweredPositionalItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.value.width_flat is not None
        width: int = self.item.value.width_flat + self.item.suffix.cell_len
        if self.item.value.annotation:
            width += COMMENT_GAP.cell_len + self.item.value.annotation.cell_len
        return width <= ctx.remaining_width

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        yield from self.item.value.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.suffix)
        if self.item.value.annotation:
            yield from ctx.render(COMMENT_GAP, self.item.value.annotation)
            yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return self.item.value.width_flat is not None


@attrs.frozen
class Break(Layout):
    item: LoweredPositionalItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        return True  # fallback

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        yield from self.item.value.render_break(ctx, annotation=True)
        yield from ctx.render(self.item.suffix)
        yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return self.item.value.width_break_begin is not None
