"""Traced repr-like containers."""

from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.stages.lowered import LoweredContainer, LoweredLeaf

from ._context import LowerContext
from ._item_base import TracedItem
from ._node_object import TracedObject


@attrs.define
class TracedContainer(TracedObject):
    """Traced container that lowers into tagged leaf or container output."""

    begin: Text
    children: list[TracedItem]
    end: Text
    indent: Text
    name: Text | None = attrs.field(default=None, kw_only=True)

    def _default_empty(self) -> Text:
        return self.begin + self.end

    empty: Text = attrs.field(
        default=attrs.Factory(_default_empty, takes_self=True), kw_only=True
    )

    @override
    def lower(self, ctx: LowerContext) -> LoweredContainer | LoweredLeaf:
        annotation: Text = self.make_annotation(ctx)
        assert self.identifier.cls is not None
        name = (
            Text(ctx.get_tag_typename(self.identifier.cls), "repr.tag_name")
            if self.name is None
            else self.name
        )
        if not self.children:
            return LoweredLeaf(
                Text.assemble(name, self.empty),
                annotation=annotation,
            )
        lowered = LoweredContainer(
            begin=Text.assemble(name, self.begin),
            children=[item.lower(ctx) for item in self.children],
            end=self.end,
            indent=self.indent,
            annotation=annotation,
        )
        return lowered
