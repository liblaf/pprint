from typing import override

import attrs
from rich.text import Text

from liblaf.pretty.literals import ELLIPSIS, EMPTY
from liblaf.pretty.stages.lower import Lowered, LoweredContainer, LoweredLeaf

from ._base import Traced
from ._context import LowerContext
from ._identifier import Identifier
from ._item import TracedItems


@attrs.define
class TracedContainer(Traced):
    begin: Text
    doc: TracedItems
    end: Text
    indent: Text = attrs.field(kw_only=True)
    hide_typename: bool = attrs.field(default=False, kw_only=True)
    has_ref: bool = attrs.field(default=False, kw_only=True)
    identifier: Identifier = attrs.field(kw_only=True)

    def _default_empty(self) -> Text:
        return Text.assemble(self.begin, self.end)

    empty: Text = attrs.field(
        default=attrs.Factory(_default_empty, takes_self=True), kw_only=True
    )

    @override
    def lower(self, ctx: LowerContext) -> Lowered:
        comment: Text = ctx.make_comment(self.identifier) if self.has_ref else EMPTY
        if self.hide_typename:
            begin_parts: list[tuple[str, str]] = []
        else:
            begin_parts: list[tuple[str, str]] = [
                (ctx.get_tag_typename(self.identifier.cls), "repr.tag_name")
            ]
        if self.doc.empty:
            return LoweredLeaf(Text.assemble(*begin_parts, self.empty), comment=comment)
        if self.doc.truncated:
            return LoweredLeaf(
                Text.assemble(*begin_parts, self.begin, ELLIPSIS, self.end),
                comment=comment,
            )
        return LoweredContainer(
            begin=Text.assemble(*begin_parts, self.begin),
            doc=self.doc.lower(ctx),
            end=self.end,
            indent=self.indent,
            comment=comment,
        )
