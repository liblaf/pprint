"""Shared base class for traced nodes that can emit reference annotations."""

import attrs
from rich.text import Text

from liblaf.pprint.common import ObjectIdentifier
from liblaf.pprint.literals import EMPTY

from ._context import LowerContext
from ._node_base import TracedNode


@attrs.define
class TracedObject(TracedNode):
    """Traced node that tracks repeated references for one object identity."""

    has_ref: bool = attrs.field(default=False, kw_only=True)
    identifier: ObjectIdentifier = attrs.field(kw_only=True)
    path: str = attrs.field(kw_only=True)

    def make_annotation(self, ctx: LowerContext) -> Text:
        """Return the `# <Type @ path>` comment shown on first appearance."""
        if not self.has_ref:
            return EMPTY
        assert self.identifier.cls is not None
        typename: str = ctx.get_ref_typename(self.identifier.cls)
        reference = (
            self.path
            if len(self.path) <= ctx.max_reference_path
            else f"{self.identifier.id_:x}"
        )
        return Text(f"# <{typename} @ {reference}>", "dim")
