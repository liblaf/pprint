import functools
from collections.abc import Sequence
from typing import override

import attrs
from rich.containers import Lines
from rich.text import Text

from liblaf.pretty.literals import COMMENT_GAP
from liblaf.pretty.stages.compile import CompileContext, Flags

from ._base import Layout, Lowered
from ._comment import CommentLayout


@attrs.frozen
class LoweredLeaf(Lowered):
    text: Text
    comment: Text

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        comment_layouts: Sequence[CommentLayout] = CommentLayout.filter_layouts(
            self.comment
        )
        if len(self.lines) == 1:
            return [
                LoweredLeafFlat(self, comment_layout)
                for comment_layout in comment_layouts
            ]
        return [
            LoweredLeafBreak(self, comment_layout) for comment_layout in comment_layouts
        ]

    @functools.cached_property
    def lines(self) -> Lines:
        return self.text.split(include_separator=True, allow_blank=True)

    @override
    def append(self, text: Text) -> Lowered:
        return attrs.evolve(self, text=self.text + text)


@attrs.frozen
class LoweredLeafFlat(Layout):
    wrapped: LoweredLeaf
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
                return Flags(multiline=True, break_before=True)

    @override
    def print(self, ctx: CompileContext) -> None:
        match self.comment_layout:
            case CommentLayout.NONE:
                ctx.print(self.wrapped.text)
            case CommentLayout.AFTER:
                ctx.print(self.wrapped.text, COMMENT_GAP, self.wrapped.comment)
            case CommentLayout.BEFORE:
                ctx.print(self.wrapped.comment, "\n", self.wrapped.text)


@attrs.frozen
class LoweredLeafBreak(Layout):
    wrapped: LoweredLeaf
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
                ctx.print(self.wrapped.text)
            case CommentLayout.AFTER:
                first_line: Text = self.wrapped.lines[0].copy()
                first_line.rstrip()
                ctx.print(
                    first_line,
                    COMMENT_GAP,
                    self.wrapped.comment,
                    "\n",
                    *self.wrapped.lines[1:],
                )
            case CommentLayout.BEFORE:
                ctx.print(self.wrapped.comment, "\n", self.wrapped.text)
