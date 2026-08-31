"""Traced `name=value` items."""

from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.literals import EQUAL
from liblaf.pprint.stages.lowered import LoweredKeyValueItem, LoweredLeaf

from ._context import LowerContext
from ._item_base import TracedItem
from ._node_base import TracedNode


@attrs.define
class TracedNameValueItem(TracedItem):
    """Traced named item stored as a styled name plus traced value."""

    name: Text
    sep: Text = attrs.field(default=EQUAL, kw_only=True)
    value: TracedNode

    def attach_value(self, value: TracedNode) -> None:
        self.value = value

    @override
    def lower(self, ctx: LowerContext) -> LoweredKeyValueItem:
        return LoweredKeyValueItem(
            prefix=self.prefix,
            key=LoweredLeaf(self.name),
            sep=self.sep,
            value=self.value.lower(ctx),
            suffix=self.suffix,
        )
