from __future__ import annotations

import abc

from liblaf.pretty.stages.lower import Lowered

from ._context import LowerContext


class Traced(abc.ABC):
    def attach(self, child: Traced) -> None:
        raise ValueError(child)

    @abc.abstractmethod
    def lower(self, ctx: LowerContext) -> Lowered: ...
