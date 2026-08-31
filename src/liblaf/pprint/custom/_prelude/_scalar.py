import types
from typing import Any

from rich.text import Text

from liblaf.pprint.custom._context import PrettyContext
from liblaf.pprint.custom._registry import registry
from liblaf.pprint.custom._repr import pretty_repr
from liblaf.pprint.stages.wrapped import WrappedLeaf


@registry.register_type(types.NoneType)
def _pretty_none(obj: None, ctx: PrettyContext) -> WrappedLeaf:
    return ctx.leaf(obj, Text("None", "repr.none"), referable=False)


@registry.register_type(types.EllipsisType)
def _pretty_ellipsis(obj: types.EllipsisType, ctx: PrettyContext) -> WrappedLeaf:
    return ctx.leaf(obj, Text("...", "repr.ellipsis"), referable=False)


@registry.register_type(bool)
def _pretty_bool(obj: bool, ctx: PrettyContext) -> WrappedLeaf:  # noqa: FBT001
    text: Text = (
        Text("True", "repr.bool_true") if obj else Text("False", "repr.bool_false")
    )
    return ctx.leaf(obj, text, referable=False)


@registry.register_type(bytearray)
@registry.register_type(bytes)
@registry.register_type(complex)
@registry.register_type(float)
@registry.register_type(int)
@registry.register_type(memoryview)
@registry.register_type(str)
def _pretty_scalar(obj: Any, ctx: PrettyContext) -> WrappedLeaf:
    return pretty_repr(obj, ctx, referable=False)
