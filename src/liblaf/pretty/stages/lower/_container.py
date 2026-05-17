import functools
from collections.abc import Sequence
from typing import Self, override

import attrs
from rich.text import Text

from liblaf.pretty.literals import COMMENT_GAP
from liblaf.pretty.stages.compile import CompileContext, Constraints, Flags

from ._base import Layout, Lowered
from ._comment import CommentLayout


@attrs.frozen
class LoweredContainer(Lowered):
    begin: Text
    doc: Lowered
    end: Text
    indent: Text
    comment: Text

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        comment_layouts: Sequence[CommentLayout] = CommentLayout.filter_layouts(
            self.comment
        )
        layouts: list[Layout] = []
        layouts.extend(
            LoweredContainerFlat(self, comment_layout)
            for comment_layout in comment_layouts
        )
        layouts.extend(
            LoweredContainerBreak(self, comment_layout)
            for comment_layout in comment_layouts
        )
        return layouts

    @override
    def append(self, text: Text) -> Self:
        return attrs.evolve(self, end=self.end + text)


@attrs.frozen
class LoweredContainerFlat(Layout):
    wrapped: LoweredContainer
    comment_layout: CommentLayout

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        match self.comment_layout:
            case CommentLayout.NONE:
                return Flags(multiline=False)
            case CommentLayout.AFTER:
                return Flags(multiline=False, break_after=True)
            case CommentLayout.BEFORE:
                return Flags(multiline=False, break_before=True)

    @override
    def print(self, ctx: CompileContext) -> None:
        match self.comment_layout:
            case CommentLayout.NONE:
                ctx.print(self.wrapped.begin)
            case CommentLayout.AFTER:
                ctx.print(self.wrapped.begin)
            case CommentLayout.BEFORE:
                ctx.print(self.wrapped.comment, "\n", self.wrapped.begin)
        self.wrapped.doc.print(ctx, Constraints.INLINE)
        match self.comment_layout:
            case CommentLayout.NONE:
                ctx.print(self.wrapped.end)
            case CommentLayout.AFTER:
                ctx.print(self.wrapped.end, COMMENT_GAP, self.wrapped.comment)
            case CommentLayout.BEFORE:
                ctx.print(self.wrapped.end)

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return super().satisfies(constraints) and self.wrapped.doc.satisfies(
            Constraints.INLINE
        )


@attrs.frozen
class LoweredContainerBreak(Layout):
    wrapped: LoweredContainer
    comment_layout: CommentLayout

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        match self.comment_layout:
            case CommentLayout.NONE:
                return Flags(multiline=True)
            case CommentLayout.AFTER:
                return Flags(multiline=True)
            case CommentLayout.BEFORE:
                return Flags(multiline=True, break_before=True)

    @override
    def print(self, ctx: CompileContext) -> None:
        match self.comment_layout:
            case CommentLayout.NONE:
                ctx.print(self.wrapped.begin)
            case CommentLayout.AFTER:
                ctx.print(self.wrapped.begin, COMMENT_GAP, self.wrapped.comment)
            case CommentLayout.BEFORE:
                ctx.print(self.wrapped.comment, "\n", self.wrapped.begin)
        with ctx.indent(self.wrapped.indent):
            ctx.newline()
            self.wrapped.doc.print(ctx, Constraints.BLOCK)
        ctx.newline()
        ctx.print(self.wrapped.end)

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return super().satisfies(constraints) and self.wrapped.doc.satisfies(
            Constraints.BLOCK
        )
