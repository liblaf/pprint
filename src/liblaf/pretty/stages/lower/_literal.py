import functools
from typing import override

import attrs
from rich.containers import Lines
from rich.text import Text

from liblaf.pretty.stages.compile import CompileContext, Flags

from ._base import Layout, Lowered


@attrs.frozen
class LoweredLiteral(Lowered):
    text: Text

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        return [LoweredLiteralLayout(self)]

    @functools.cached_property
    def lines(self) -> Lines:
        return self.text.split(include_separator=True, allow_blank=True)

    @override
    def append(self, text: Text) -> Lowered:
        return attrs.evolve(self, text=self.text + text)


@attrs.frozen
class LoweredLiteralLayout(Layout):
    wrapped: LoweredLiteral

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        return Flags(multiline=len(self.wrapped.lines) > 1)

    @override
    def print(self, ctx: CompileContext) -> None:
        ctx.print(self.wrapped.text)
