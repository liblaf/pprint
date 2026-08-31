"""Wrapped positional items."""

from typing import Self, override

import attrs

from liblaf.pprint.stages.traced import TRACED_MISSING, TracedPositionalItem

from ._base import WrappedChild
from ._context import TraceContext
from ._item_base import WrappedItem
from ._node_base import WrappedNode
from ._node_leaf import WrappedLeaf


@attrs.define
class WrappedPositionalItem(WrappedItem):
    """Wrapped positional item used for ordinary children and ellipses."""

    value: WrappedNode

    @classmethod
    def ellipsis(cls) -> Self:
        return cls(value=WrappedLeaf.ellipsis())

    @override
    def trace(
        self, ctx: TraceContext
    ) -> tuple[tuple[WrappedChild], TracedPositionalItem]:
        traced: TracedPositionalItem = TracedPositionalItem(
            prefix=self.prefix, value=TRACED_MISSING, suffix=self.suffix
        )
        child: WrappedChild = WrappedChild(
            wrapped=self.value,
            depth=ctx.depth,
            attach=traced.attach,  # ty:ignore[invalid-argument-type]
            path=ctx.path + self.path_segment,
        )
        return (child,), traced
