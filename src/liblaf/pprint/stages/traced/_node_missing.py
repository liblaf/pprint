"""Placeholder node used before traced children are attached."""

from typing import NoReturn, override

import attrs

from ._context import LowerContext
from ._node_base import TracedNode


@attrs.define
class TracedMissingType(TracedNode):
    """Sentinel traced node that should never survive to lowering."""

    @override
    def lower(self, ctx: LowerContext) -> NoReturn:
        raise NotImplementedError


TRACED_MISSING: TracedMissingType = TracedMissingType()
"""Placeholder instance used while traced items are being assembled."""
