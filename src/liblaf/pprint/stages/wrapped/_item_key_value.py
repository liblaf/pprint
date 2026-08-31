"""Wrapped `key: value` items."""

from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.literals import COLON
from liblaf.pprint.stages.traced import TRACED_MISSING, TracedKeyValueItem

from ._base import WrappedChild
from ._context import TraceContext
from ._item_base import WrappedItem
from ._node_base import WrappedNode


@attrs.define
class WrappedKeyValueItem(WrappedItem):
    """Wrapped mapping-style item whose key and value trace independently."""

    key: WrappedNode
    sep: Text = attrs.field(default=COLON, kw_only=True)
    value: WrappedNode
    path_key: str = attrs.field(default="?", kw_only=True)

    @override
    def trace(
        self, ctx: TraceContext
    ) -> tuple[tuple[WrappedChild, WrappedChild], TracedKeyValueItem]:
        traced: TracedKeyValueItem = TracedKeyValueItem(
            prefix=self.prefix,
            key=TRACED_MISSING,
            sep=self.sep,
            value=TRACED_MISSING,
            suffix=self.suffix,
        )
        key: WrappedChild = WrappedChild(
            wrapped=self.key,
            depth=ctx.depth,
            attach=traced.attach_key,  # ty:ignore[invalid-argument-type]
            path=ctx.path + ".<key>",
        )
        value: WrappedChild = WrappedChild(
            wrapped=self.value,
            depth=ctx.depth,
            attach=traced.attach_value,  # ty:ignore[invalid-argument-type]
            path=ctx.path + f"[{self.path_key}]",
        )
        return (key, value), traced
