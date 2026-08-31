"""Lowered repr-like containers."""

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
class LoweredContainer(LoweredNode):
    """Lowered container with begin and end tags plus child items."""

    begin: Text
    children: list[LoweredItem]
    end: Text
    indent: Text

    @override
    def layouts(self) -> Generator[Layout]:
        yield ContainerFlat(self)
        yield ContainerBreak(self)

    @override
    def render_flat(
        self, ctx: CompileContext, *, annotation: bool = False
    ) -> RenderResult:
        yield from ctx.render(self.begin)
        for item in self.children:
            yield from item.render(ctx)
        yield from ctx.render(self.end)
        if annotation and self.annotation:
            yield from ctx.render(COMMENT_GAP, self.annotation)

    @override
    def render_break(
        self, ctx: CompileContext, *, annotation: bool = True
    ) -> RenderResult:
        yield from ctx.render(self.begin)
        if annotation and self.annotation:
            yield from ctx.render(COMMENT_GAP, self.annotation)
        yield from ctx.ensure_newline()
        with ctx.indent(self.indent):
            for item in self.children:
                yield from item.render(ctx)
        yield from ctx.ensure_newline()
        yield from ctx.render(self.end)

    @functools.cached_property
    @override
    def width_break_begin(self) -> int:
        return self.begin.cell_len

    @functools.cached_property
    @override
    def width_break_end(self) -> int:
        return self.end.cell_len

    @functools.cached_property
    @override
    def width_flat(self) -> int | None:
        result: int = self.begin.cell_len
        for item in self.children:
            if item.width_inline is None:
                return None
            result += item.width_inline
        result += self.end.cell_len
        return result


@attrs.frozen
class ContainerFlat(Layout):
    node: LoweredContainer

    @override
    def fits(self, ctx: CompileContext) -> bool:
        assert self.node.width_flat is not None
        width: int = self.node.width_flat
        if self.node.annotation:
            width += COMMENT_GAP.cell_len + self.node.annotation.cell_len
        return width <= ctx.remaining_width

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        return self.node.render_flat(ctx, annotation=True)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return self.node.width_flat is not None


@attrs.frozen
class ContainerBreak(Layout):
    node: LoweredContainer

    @override
    def fits(self, ctx: CompileContext) -> bool:
        return True  # fallback

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        return self.node.render_break(ctx, annotation=True)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return True
