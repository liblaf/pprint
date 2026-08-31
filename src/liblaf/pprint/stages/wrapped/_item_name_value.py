"""Wrapped `name=value` items."""

from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.literals import EQUAL
from liblaf.pprint.stages.traced import TRACED_MISSING, TracedNameValueItem

from ._base import WrappedChild
from ._context import TraceContext
from ._item_base import WrappedItem
from ._node_base import WrappedNode


@attrs.define
class WrappedNameValueItem(WrappedItem):
    """Wrapped named item whose name is already represented as styled text."""

    name: Text
    sep: Text = attrs.field(default=EQUAL, kw_only=True)
    value: WrappedNode

    @override
    def trace(
        self, ctx: TraceContext
    ) -> tuple[tuple[WrappedChild], TracedNameValueItem]:
        traced: TracedNameValueItem = TracedNameValueItem(
            prefix=self.prefix,
            name=self.name,
            sep=self.sep,
            value=TRACED_MISSING,
            suffix=self.suffix,
        )
        child: WrappedChild = WrappedChild(
            wrapped=self.value,
            depth=ctx.depth,
            attach=traced.attach_value,  # ty:ignore[invalid-argument-type]
            path=ctx.path + "." + self.name.plain,
        )
        return (child,), traced
