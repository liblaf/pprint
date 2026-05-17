from typing import override

import attrs
from rich.text import Text

from liblaf.pretty.stages.lower import Lowered, LoweredKeyValue

from ._base import Traced
from ._context import LowerContext


@attrs.frozen
class TracedKeyValue(Traced):
    key: Traced
    separator: Text
    value: Traced

    @override
    def lower(self, ctx: LowerContext) -> Lowered:
        return LoweredKeyValue(
            key=self.key.lower(ctx),
            separator=self.separator,
            value=self.value.lower(ctx),
        )
