import attrs
from rich.text import Text

from liblaf.pretty.stages.lower import Lowered, LoweredLiteral

from ._base import Traced
from ._context import LowerContext
from ._identifier import Identifier


@attrs.frozen
class TracedRef(Traced):
    identifier: Identifier

    def lower(self, ctx: LowerContext) -> Lowered:
        assert self.identifier.cls is not None
        return LoweredLiteral(
            Text.assemble(
                ("<", "repr.tag_start"),
                (ctx.get_ref_typename(self.identifier.cls), "repr.tag_name"),
                " @ ",
                self.identifier.path.__rich__(),
                (">", "repr.tag_end"),
            )
        )
