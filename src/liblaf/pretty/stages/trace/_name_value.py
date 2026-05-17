import attrs
from rich.text import Text

from liblaf.pretty.stages.lower import Lowered, LoweredKeyValue, LoweredLiteral

from ._base import Traced
from ._context import LowerContext


@attrs.define
class NameValue(Traced):
    name: Text
    separator: Text
    value: Traced

    def lower(self, ctx: LowerContext) -> Lowered:
        return LoweredKeyValue(
            key=LoweredLiteral(self.name),
            separator=self.separator,
            value=self.value.lower(ctx),
        )
