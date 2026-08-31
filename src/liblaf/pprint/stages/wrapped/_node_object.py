"""Shared base class for wrapped nodes that participate in reference tracking."""

import attrs

from liblaf.pprint.stages.traced import TracedRef

from ._context import TraceContext
from ._node_base import WrappedNode


@attrs.define
class WrappedObject(WrappedNode):
    """Wrapped node that can emit a traced reference on repeated visits."""

    referencable: bool = attrs.field(default=True, kw_only=True)

    def visit(self, ctx: TraceContext) -> TracedRef | None:
        """Record this object's type and return a reference when seen before."""
        if self.identifier.cls is not None:
            ctx.types.add(self.identifier.cls)
        if (
            self.referencable
            and self.identifier.id_ is not None
            and (anchor := ctx.trace_cache.get(self.identifier.id_)) is not None
        ):
            anchor.has_ref = True
            return TracedRef(identifier=self.identifier, path=anchor.path)
        return None
