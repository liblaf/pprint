from __future__ import annotations

import contextlib
import types
from typing import Protocol, Self

import attrs
from rich.console import Console, ConsoleOptions
from rich.segment import Segment

from ._segments import Prefix, Segments


@attrs.frozen
class CompileContextSnapshot:
    column: int
    console: Console
    options: ConsoleOptions
    prefix: Prefix


@attrs.frozen
class Compiled(Segments):
    context: CompileContextSnapshot = attrs.field(kw_only=True)
    fits: bool = attrs.field(kw_only=True)


@attrs.define
class Capture(contextlib.AbstractContextManager):
    context: Context = attrs.field()
    data: list[Segment] = attrs.field(factory=list, init=False)
    fits: bool = attrs.field(default=True, init=False)
    snapshot: CompileContextSnapshot | None = attrs.field(default=None, init=False)

    def __enter__(self) -> Self:
        self.context.captures.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.context.captures.pop()
        self.snapshot = self.context.snapshot()

    def get(self) -> Compiled:
        assert self.snapshot is not None
        return Compiled(self.data, context=self.snapshot, fits=self.fits)


class Context(Protocol):
    captures: list[Capture]

    def snapshot(self) -> CompileContextSnapshot: ...
