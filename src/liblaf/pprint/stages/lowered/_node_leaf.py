"""Lowered scalar leaves."""

import functools
from collections.abc import Generator
from typing import Self, override

import attrs
from rich.console import RenderResult
from rich.containers import Lines
from rich.text import Text

from liblaf.pprint.literals import COMMENT_GAP, ELLIPSIS

from ._context import CompileContext
from ._layout import Layout
from ._node_base import LoweredNode


@attrs.frozen
class LoweredLeaf(LoweredNode):
    """Lowered scalar text value, optionally annotated with a shared reference."""

    value: Text

    @classmethod
    def ellipsis(cls) -> Self:
        return cls(ELLIPSIS)

    @functools.cached_property
    def lines(self) -> Lines:
        return self.value.split(include_separator=True, allow_blank=True)

    @override
    def layouts(self) -> Generator[Layout]:
        if len(self.lines) == 1:
            yield LeafFlat(self)
        else:
            yield LeafBreak(self)

    @override
    def render_flat(
        self, ctx: CompileContext, *, annotation: bool = False
    ) -> RenderResult:
        assert len(self.lines) == 1
        yield from ctx.render(self.value)
        if annotation and self.annotation:
            yield from ctx.render(COMMENT_GAP, self.annotation)

    @override
    def render_break(
        self, ctx: CompileContext, *, annotation: bool = True
    ) -> RenderResult:
        assert len(self.lines) > 1
        if annotation and self.annotation:
            first_line: Text = self.lines[0].copy()
            first_line.rstrip()
            yield from ctx.render(first_line)
            yield from ctx.render(COMMENT_GAP, self.annotation)
            yield from ctx.ensure_newline()
            for line in self.lines[1:]:
                yield from ctx.render(line)
        else:
            yield from ctx.render(self.value)

    @functools.cached_property
    @override
    def width_break_begin(self) -> int | None:
        if len(self.lines) == 1:
            return None
        return self.lines[0].cell_len

    @functools.cached_property
    @override
    def width_break_end(self) -> int | None:
        if len(self.lines) == 1:
            return None
        return self.lines[-1].cell_len

    @functools.cached_property
    @override
    def width_flat(self) -> int | None:
        if len(self.lines) > 1:
            return None
        return self.value.cell_len


@attrs.frozen
class LeafFlat(Layout):
    node: LoweredLeaf

    @override
    def fits(self, ctx: CompileContext) -> bool:
        return True  # fallback

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from self.node.render_flat(ctx, annotation=True)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return len(self.node.lines) == 1


@attrs.frozen
class LeafBreak(Layout):
    node: LoweredLeaf

    @override
    def fits(self, ctx: CompileContext) -> bool:
        return True  # fallback

    @override
    def render(self, ctx: CompileContext) -> RenderResult:
        yield from self.node.render_break(ctx, annotation=True)

    @override
    def supports(self, ctx: CompileContext) -> bool:
        return len(self.node.lines) > 1
