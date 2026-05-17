import functools
from typing import override

import attrs
from rich.text import Text

from liblaf.pretty.stages.compile import CompileContext, Constraints, Flags

from ._base import Layout, Lowered


@attrs.frozen
class LoweredKeyValue(Lowered):
    key: Lowered
    separator: Text
    value: Lowered

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        return [LoweredKeyValueFlat(self), LoweredKeyValueBreak(self)]

    @override
    def append(self, text: Text) -> Lowered:
        return attrs.evolve(self, value=self.value.append(text))


@attrs.frozen
class LoweredKeyValueFlat(Layout):
    wrapped: LoweredKeyValue

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        return Flags.INLINE

    @override
    def print(self, ctx: CompileContext) -> None:
        self.wrapped.key.print(ctx, Constraints.INLINE)
        ctx.print(self.wrapped.separator)
        self.wrapped.value.print(ctx, Constraints.INLINE)

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return (
            super().satisfies(constraints)
            and self.wrapped.key.satisfies(Constraints.INLINE)
            and self.wrapped.value.satisfies(Constraints.INLINE)
        )


@attrs.frozen
class LoweredKeyValueBreak(Layout):
    wrapped: LoweredKeyValue

    @functools.cached_property
    @override
    def flags(self) -> Flags:
        return Flags.BLOCK

    @override
    def print(self, ctx: CompileContext) -> None:
        self.wrapped.key.print(ctx, Constraints.KEY)
        ctx.print(self.wrapped.separator)
        self.wrapped.value.print(ctx, Constraints.VALUE)

    @override
    def satisfies(self, constraints: Constraints) -> bool:
        return (
            super().satisfies(constraints)
            and self.wrapped.key.satisfies(Constraints.KEY)
            and self.wrapped.value.satisfies(Constraints.VALUE)
        )
