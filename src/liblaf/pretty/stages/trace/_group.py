import attrs

from liblaf.pretty.literals import ELLIPSIS, EMPTY
from liblaf.pretty.stages.lower import Lowered, LoweredGroup, LoweredLiteral

from ._context import LowerContext
from ._item import TracedItems


@attrs.define
class TracedGroup(TracedItems):
    def lower(self, ctx: LowerContext) -> Lowered:
        if self.empty:
            return LoweredLiteral(EMPTY)
        if self.truncated:
            return LoweredLiteral(ELLIPSIS)
        assert isinstance(self.children, list)
        return LoweredGroup([child.lower(ctx) for child in self.children])
