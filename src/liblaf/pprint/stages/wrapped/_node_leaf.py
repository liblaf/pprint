"""Wrapped scalar leaves."""

from typing import Self, override

import attrs
from rich.text import Text

from liblaf.pprint.common import ObjectIdentifier
from liblaf.pprint.literals import ELLIPSIS
from liblaf.pprint.stages.traced import TracedLeaf, TracedNode

from ._context import TraceContext
from ._node_object import WrappedObject


@attrs.define
class WrappedLeaf(WrappedObject):
    """Wrapped scalar text node with an ellipsis constructor."""

    value: Text

    @classmethod
    def ellipsis(cls) -> Self:
        return cls(
            value=ELLIPSIS,
            identifier=ObjectIdentifier.from_obj(...),
            referencable=False,
        )

    @override
    def trace(self, ctx: TraceContext) -> tuple[tuple[()], TracedNode]:
        if (ref := self.visit(ctx)) is not None:
            return (), ref
        traced = TracedLeaf(value=self.value, identifier=self.identifier, path=ctx.path)
        if self.identifier.id_ is not None:
            ctx.trace_cache[self.identifier.id_] = traced
        return (), traced
