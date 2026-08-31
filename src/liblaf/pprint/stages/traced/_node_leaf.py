"""Traced scalar leaves."""

from typing import Self, override

import attrs
from rich.text import Text

from liblaf.pprint.common import ObjectIdentifier
from liblaf.pprint.literals import ELLIPSIS
from liblaf.pprint.stages.lowered import LoweredLeaf

from ._context import LowerContext
from ._node_object import TracedObject


@attrs.define
class TracedLeaf(TracedObject):
    """Traced scalar text value with helpers for literals and ellipses."""

    value: Text

    @classmethod
    def ellipsis(cls) -> Self:
        return cls(
            ELLIPSIS,
            has_ref=False,
            identifier=ObjectIdentifier.from_obj(...),
            path="$",
        )

    @classmethod
    def literal(cls, text: Text) -> Self:
        return cls(text, has_ref=False, identifier=ObjectIdentifier.missing(), path="$")

    @override
    def lower(self, ctx: LowerContext) -> LoweredLeaf:
        annotation: Text = self.make_annotation(ctx)
        return LoweredLeaf(self.value, annotation=annotation)
