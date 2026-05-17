import functools
from collections.abc import Sequence
from typing import Self, override

import attrs
from rich.text import Text

from liblaf.pretty.stages.compile import CompileContext, Constraints, Flags

from ._base import Layout, Lowered
from ._item import LoweredItem


@attrs.frozen
class LoweredGroup(Lowered):
    children: Sequence[LoweredItem]

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        return [LoweredGroupFlat(self), LoweredGroupBreak(self)]

    @override
    def append(self, text: Text) -> Self:
        return attrs.evolve(
            self, children=[*self.children[:-1], self.children[-1].append(text)]
        )


@attrs.frozen
class LoweredGroupFlat(Layout):
    wrapped: LoweredGroup

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        return Flags.INLINE

    @override
    def print(self, ctx: CompileContext) -> None:
        for child in self.wrapped.children:
            child.wrapped.print(ctx, Constraints.INLINE)
            ctx.print(child.flat_gap)

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return super().satisfies(constraints) and all(
            child.wrapped.satisfies(Constraints.INLINE)
            for child in self.wrapped.children
        )


@attrs.frozen
class LoweredGroupBreak(Layout):
    wrapped: LoweredGroup

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        return Flags.BLOCK

    @override
    def print(self, ctx: CompileContext) -> None:
        for i, child in enumerate(self.wrapped.children):
            child.wrapped.print(ctx, Constraints.BLOCK)
            if i < len(self.wrapped.children) - 1:
                ctx.newline()

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return super().satisfies(constraints) and all(
            child.wrapped.satisfies(Constraints.BLOCK)
            for child in self.wrapped.children
        )
