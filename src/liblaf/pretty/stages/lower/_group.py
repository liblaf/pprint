from typing import override

import attrs
from rich.text import Text

from liblaf.pretty.stages.compile import CompileContext, Constraints, Hints

from ._base import Candidate, Lowered


@attrs.frozen
class LoweredGroup(Lowered):
    begin: Text
    doc: Lowered
    end: Text


@attrs.frozen
class LoweredGroupFlat(Candidate):
    __wrapped__: Lowered

    @override
    def print(self, ctx: CompileContext, constraints: Constraints) -> None:
        ctx.print(self.wrapped.begin)
        self.wrapped.print(ctx, constraints)
        ctx.print(self.wrapped.end)
