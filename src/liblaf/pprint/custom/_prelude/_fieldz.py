from collections.abc import Callable, Sequence
from typing import Any

import fieldz
from rich.repr import RichReprResult
from rich.text import Text

from liblaf.pprint.custom._context import PrettyContext
from liblaf.pprint.custom._registry import registry
from liblaf.pprint.stages.wrapped import WrappedContainer, WrappedItem


@registry.register_func
def _describe_fieldz(obj: Any, ctx: PrettyContext) -> WrappedContainer | None:
    try:
        fields: Sequence[fieldz.Field] = fieldz.fields(obj)
    except TypeError:
        return None
    children: list[WrappedItem] = []
    for field in fields:
        if not field.repr:
            continue
        value: Any = getattr(obj, field.name, fieldz.Field.MISSING)
        if ctx.options.hide_defaults and _safe_equal(value, field.default):
            continue
        children.append(ctx.name_value(field.name, value))
    children: list[WrappedItem] = ctx.add_separators(children)
    return ctx.container(
        obj=obj,
        begin=Text("(", "tag_start"),
        children=children,
        end=Text(")", "tag_end"),
    )


@registry.register_func
def _describe_rich_repr(obj: Any, ctx: PrettyContext) -> WrappedContainer | None:
    rich_repr: Callable[[], RichReprResult | None] | None = getattr(
        obj, "__rich_repr__", None
    )
    if rich_repr is None:
        return None
    result: RichReprResult | None = rich_repr()
    if result is None:
        return None
    children: list[WrappedItem] = []
    for item in result:
        match item:
            case (name, value, default):
                if ctx.options.hide_defaults and _safe_equal(value, default):
                    continue
                children.append(ctx.name_value(name, value))
            case (name, value):
                children.append(ctx.name_value(name, value))
            case (value,):
                children.append(ctx.positional(value))
            case value:
                children.append(ctx.positional(value))
    children: list[WrappedItem] = ctx.add_separators(children)
    return ctx.container(
        obj=obj,
        begin=Text("(", "tag_start"),
        children=children,
        end=Text(")", "tag_end"),
    )


def _safe_equal(a: Any, b: Any) -> bool:
    if a is b:
        return True
    try:
        return a == b
    except Exception:  # noqa: BLE001
        return False
