import attrs
from rich.text import Text

from liblaf.pretty.literals import EMPTY
from liblaf.pretty.stages.lower import Lowered, LoweredLeaf

from ._base import Traced
from ._context import LowerContext
from ._identifier import Identifier


@attrs.define
class TracedLeaf(Traced):
    text: Text
    has_ref: bool = attrs.field(default=False, kw_only=True)
    identifier: Identifier = attrs.field(kw_only=True)

    def lower(self, ctx: LowerContext) -> Lowered:
        return LoweredLeaf(
            self.text,
            comment=ctx.make_comment(self.identifier) if self.has_ref else EMPTY,
        )
