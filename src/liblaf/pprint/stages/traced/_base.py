"""Reference-aware intermediate nodes and items."""

import abc

from liblaf.pprint.stages.lowered import Lowered

from ._context import LowerContext


class Traced(abc.ABC):
    """Interface implemented by traced values that can lower into renderables."""

    @abc.abstractmethod
    def lower(self, ctx: LowerContext) -> Lowered: ...
