"""Lowered `key: value` and `name=value` item layouts."""

import functools
from collections.abc import Generator
from typing import override

import attrs
from rich.console import RenderResult
from rich.text import Text

from liblaf.pprint.literals import COMMENT_GAP

from ._context import CompileContext
from ._item_base import LoweredItem
from ._layout import Layout
from ._node_base import LoweredNode


@attrs.frozen
class LoweredKeyValueItem(LoweredItem):
    """Lowered mapping-style item with several layout strategies."""

    key: LoweredNode
    sep: Text
    value: LoweredNode

    @functools.cached_property
    @override
    def width_inline(self) -> int | None:
        if (
            self.key.annotation
            or self.value.annotation
            or self.key.width_flat is None
            or self.value.width_flat is None
        ):
            return None
        return (
            +self.prefix.cell_len
            + self.key.width_flat
            + self.sep.cell_len
            + self.value.width_flat
            + self.suffix.cell_len
        )

    @override
    def layouts(self) -> Generator[Layout]:
        yield Inline(self)
        yield FlatFlat(self)
        yield FlatBreak(self)
        yield BreakFlat(self)
        yield BreakBreak(self)


@attrs.frozen
class Inline(Layout):
    item: LoweredKeyValueItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.key.width_flat is not None
        assert self.item.value.width_flat is not None
        return (
            self.item.prefix.cell_len
            + self.item.key.width_flat
            + self.item.sep.cell_len
            + self.item.value.width_flat
            + self.item.suffix.cell_len
            <= ctx.remaining_width
        )

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.render(self.item.prefix)
        yield from self.item.key.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.sep)
        yield from self.item.value.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.suffix)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return (
            ctx.column > 0
            and not self.item.key.annotation
            and not self.item.value.annotation
            and self.item.key.width_flat is not None
            and self.item.value.width_flat is not None
        )


@attrs.frozen
class FlatFlat(Layout):
    item: LoweredKeyValueItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.key.width_flat is not None
        assert self.item.value.width_flat is not None
        width: int = (
            self.item.key.width_flat
            + self.item.sep.cell_len
            + self.item.value.width_flat
        )
        if self.item.value.annotation:
            width += COMMENT_GAP.cell_len + self.item.value.annotation.cell_len
        width += self.item.suffix.cell_len
        return width <= ctx.remaining_width

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        if self.item.key.annotation:
            yield from ctx.render(self.item.key.annotation)
            yield from ctx.ensure_newline()
        yield from self.item.key.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.sep)
        yield from self.item.value.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.suffix)
        if self.item.value.annotation:
            yield from ctx.render(COMMENT_GAP, self.item.value.annotation)
        if self.item.key.annotation or self.item.value.annotation:
            yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return (
            self.item.key.width_flat is not None
            and self.item.value.width_flat is not None
        )


@attrs.frozen
class FlatBreak(Layout):
    item: LoweredKeyValueItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.key.width_flat is not None
        assert self.item.value.width_break_begin is not None
        width: int = (
            self.item.key.width_flat
            + self.item.sep.cell_len
            + self.item.value.width_break_begin
        )
        if self.item.value.annotation:
            width += COMMENT_GAP.cell_len + self.item.value.annotation.cell_len
        return width <= ctx.remaining_width

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        if self.item.key.annotation:
            yield from ctx.render(self.item.key.annotation)
            yield from ctx.ensure_newline()
        yield from self.item.key.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.sep)
        yield from self.item.value.render_break(ctx, annotation=True)
        yield from ctx.render(self.item.suffix)
        yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return (
            self.item.key.width_flat is not None
            and self.item.value.width_break_begin is not None
        )


@attrs.frozen
class BreakFlat(Layout):
    item: LoweredKeyValueItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.item.key.width_break_end is not None
        assert self.item.value.width_flat is not None
        width: int = (
            self.item.key.width_break_end
            + self.item.sep.cell_len
            + self.item.value.width_flat
        )
        if self.item.value.annotation:
            width += COMMENT_GAP.cell_len + self.item.value.annotation.cell_len
        width += self.item.suffix.cell_len
        return width <= ctx.remaining_width

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        yield from self.item.key.render_break(ctx, annotation=True)
        yield from ctx.render(self.item.sep)
        yield from self.item.value.render_flat(ctx, annotation=False)
        yield from ctx.render(self.item.suffix)
        if self.item.value.annotation:
            yield from ctx.render(COMMENT_GAP, self.item.value.annotation)
        yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return (
            self.item.key.width_break_end is not None
            and self.item.value.width_flat is not None
        )


@attrs.frozen
class BreakBreak(Layout):
    item: LoweredKeyValueItem

    @override
    def fits(self, ctx: CompileContext) -> bool:
        return True  # fallback

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from ctx.ensure_newline()
        yield from self.item.key.render_break(ctx, annotation=True)
        yield from ctx.render(self.item.sep)
        yield from self.item.value.render_break(ctx, annotation=True)
        yield from ctx.render(self.item.suffix)
        yield from ctx.ensure_newline()

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return (
            self.item.key.width_break_end is not None
            and self.item.value.width_break_begin is not None
        )
