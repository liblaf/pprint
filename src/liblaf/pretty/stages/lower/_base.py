from __future__ import annotations

import abc
import functools

import attrs

from liblaf.pretty.stages.compile import (
    CompileContext,
    Compiled,
    Constraints,
    Hints,
    StopReason,
)


@attrs.define
class Candidate(abc.ABC):
    __wrapped__: Lowered

    @abc.abstractmethod
    @functools.cached_property
    def flags_hint(self) -> Hints: ...

    @abc.abstractmethod
    def print(self, ctx: CompileContext, constraints: Constraints) -> None: ...

    def render(
        self,
        ctx: CompileContext,
        *,
        constraints: Constraints,
        stop: StopReason | None = None,
    ) -> Compiled:
        with ctx.capture(stop=stop) as capture:
            self.print(ctx, constraints=constraints)
        return capture.get()


@attrs.define
class Lowered:
    @abc.abstractmethod
    def candidates(self, constraints: Constraints) -> list[Candidate]: ...
