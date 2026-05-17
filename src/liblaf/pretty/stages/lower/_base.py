import abc
import functools
from collections.abc import Iterable, Sequence
from typing import Self

import attrs
from rich.text import Text

from liblaf.pretty.stages.compile import CompileContext, Compiled, Constraints, Flags


@attrs.frozen
class Layout(abc.ABC):
    @functools.cached_property
    @abc.abstractmethod
    def flags(self) -> Flags: ...

    def preview(self, ctx: CompileContext) -> Compiled:
        ctx: CompileContext = ctx.clone()
        with ctx.capture() as capture:
            self.print(ctx)
        return capture.get()

    @abc.abstractmethod
    def print(self, ctx: CompileContext) -> None: ...

    def satisfies(self, constraints: Constraints) -> bool:
        return constraints.allow(self.flags)


@attrs.frozen
class Lowered(abc.ABC):
    @abc.abstractmethod
    @functools.cached_property
    def layouts(self) -> Sequence[Layout]: ...

    @abc.abstractmethod
    def append(self, text: Text) -> Self: ...

    def print(
        self, ctx: CompileContext, constraints: Constraints = Constraints.BLOCK
    ) -> None:
        compiled: Compiled | None = None
        for layout in self.filter_layouts(constraints):
            compiled: Compiled = layout.preview(ctx)
            if compiled.fits:
                ctx.commit(compiled)
                return
        if compiled is None:
            raise ValueError(constraints)
        ctx.commit(compiled)

    def filter_layouts(self, constraints: Constraints) -> Iterable[Layout]:
        for layout in self.layouts:
            if layout.satisfies(constraints):
                yield layout

    def preview(
        self, ctx: CompileContext, constraints: Constraints = Constraints.BLOCK
    ) -> Compiled:
        ctx: CompileContext = ctx.clone()
        with ctx.capture() as capture:
            self.print(ctx, constraints)
        return capture.get()

    def satisfies(self, constraints: Constraints) -> bool:
        for _ in self.filter_layouts(constraints):
            return True
        return False
