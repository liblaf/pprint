from typing import Any

from rich.text import Text

from liblaf.pprint.custom._context import PrettyContext
from liblaf.pprint.custom._registry import registry
from liblaf.pprint.literals import COMMA
from liblaf.pprint.stages.wrapped import WrappedContainer, WrappedItem


@registry.register_type(dict)
def _pretty_dict(obj: dict[Any, Any], ctx: PrettyContext) -> WrappedContainer:
    children: list[WrappedItem] = [
        ctx.key_value(key, value)
        for key, value in ctx.truncate_dict(ctx.possibly_sorted(obj.items()))
    ]
    return ctx.container(
        obj=obj,
        begin=Text("{", "repr.tag_start"),
        children=children,
        end=Text("}", "repr.tag_end"),
    )


@registry.register_type(frozenset)
def _pretty_frozenset(obj: frozenset[Any], ctx: PrettyContext) -> WrappedContainer:
    children: list[WrappedItem] = [
        ctx.positional(item) for item in ctx.truncate_list(ctx.possibly_sorted(obj))
    ]
    return ctx.container(
        obj=obj,
        begin=Text("({", "repr.tag_start"),
        children=children,
        end=Text("})", "repr.tag_end"),
        empty=Text.assemble(
            ("(", "repr.tag_start"),
            (")", "repr.tag_end"),
        ),
    )


@registry.register_type(list)
def _pretty_list(obj: list[Any], ctx: PrettyContext) -> WrappedContainer:
    children: list[WrappedItem] = [
        ctx.positional(item) for item in ctx.truncate_list(obj)
    ]
    return ctx.container(
        obj=obj,
        begin=Text("[", "repr.tag_start"),
        children=children,
        end=Text("]", "repr.tag_end"),
    )


@registry.register_type(set)
def _pretty_set(obj: set[Any], ctx: PrettyContext) -> WrappedContainer:
    children: list[WrappedItem] = [
        ctx.positional(item) for item in ctx.truncate_list(ctx.possibly_sorted(obj))
    ]
    return ctx.container(
        obj=obj,
        begin=Text("{", "repr.tag_start"),
        children=children,
        end=Text("}", "repr.tag_end"),
        empty=Text.assemble(
            ("set", "repr.tag_name"),
            ("(", "repr.tag_start"),
            (")", "repr.tag_end"),
        ),
    )


@registry.register_type(tuple)
def _pretty_tuple(obj: tuple[Any, ...], ctx: PrettyContext) -> WrappedContainer:
    children: list[WrappedItem] = [
        ctx.positional(item) for item in ctx.truncate_list(obj)
    ]
    children: list[WrappedItem] = ctx.add_separators(children)
    if len(children) == 1:
        children[-1].suffix = COMMA
    return ctx.container(
        obj=obj,
        begin=Text("(", "repr.tag_start"),
        children=children,
        end=Text(")", "repr.tag_end"),
        add_separators=False,
        referable=False,
    )
