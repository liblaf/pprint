import attrs
from rich.text import Text

from liblaf.pretty.common import TRUNCATED, TruncatedType
from liblaf.pretty.stages.lower import LoweredItem

from ._base import Traced
from ._context import LowerContext


@attrs.frozen
class Separator:
    delimiter: Text
    flat_gap: Text


@attrs.define
class TracedItem(Traced):
    wrapped: Traced
    separator: Separator

    def lower(self, ctx: LowerContext) -> LoweredItem:
        return LoweredItem(
            self.wrapped.lower(ctx).append(self.separator.delimiter),
            flat_gap=self.separator.flat_gap,
        )


@attrs.define
class TracedItems(Traced):
    children: list[TracedItem] | TruncatedType

    @property
    def empty(self) -> bool:
        return isinstance(self.children, list) and len(self.children) == 0

    @property
    def truncated(self) -> bool:
        return self.children is TRUNCATED
