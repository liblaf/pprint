"""Reference nodes emitted for repeated referencable objects."""

from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.common import ObjectIdentifier
from liblaf.pprint.stages.lowered import LoweredLeaf

from ._context import LowerContext
from ._node_base import TracedNode


@attrs.define
class TracedRef(TracedNode):
    """Traced node that lowers into a `<Type @ path>` reference tag."""

    identifier: ObjectIdentifier
    path: str

    @override
    def lower(self, ctx: LowerContext) -> LoweredLeaf:
        assert self.identifier.cls is not None
        typename: str = ctx.get_ref_typename(self.identifier.cls)
        reference = (
            self.path
            if len(self.path) <= ctx.max_reference_path
            else f"{self.identifier.id_:x}"
        )
        return LoweredLeaf(
            Text.assemble(
                ("<", "repr.tag_start"),
                (typename, "repr.tag_name"),
                (f" @ {reference}", "repr.tag_contents"),
                (">", "repr.tag_end"),
            )
        )
