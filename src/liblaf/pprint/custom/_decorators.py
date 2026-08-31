"""Declarative container decorators for custom pretty-printers."""

from __future__ import annotations

import builtins
import functools
from collections.abc import Callable, Iterable

from rich.text import Text

from liblaf.pprint.stages.wrapped import WrappedItem, WrappedNode

from ._context import PrettyContext

type ItemProducer[T] = Callable[[T, PrettyContext], Iterable[WrappedItem | None]]


def container[T](
    *,
    name: str | Text | None = None,
    begin: str | Text = "(",
    end: str | Text = ")",
    referable: bool = True,
) -> Callable[[ItemProducer[T]], Callable[[T, PrettyContext], WrappedNode]]:
    """Turn an item-producing pretty function into an object container."""
    return _container_decorator(
        name=name,
        begin=begin,
        end=end,
        referable=referable,
        limit_option=None,
    )


def list_container[T](
    *,
    name: str | Text | None = None,
    begin: str | Text = "[",
    end: str | Text = "]",
    referable: bool = True,
) -> Callable[[ItemProducer[T]], Callable[[T, PrettyContext], WrappedNode]]:
    """Build a list-shaped custom formatter bounded by `max_list`."""
    return _container_decorator(
        name=name,
        begin=begin,
        end=end,
        referable=referable,
        limit_option="max_list",
    )


def dict_container[T](
    *,
    name: str | Text | None = None,
    begin: str | Text = "{",
    end: str | Text = "}",
    referable: bool = True,
) -> Callable[[ItemProducer[T]], Callable[[T, PrettyContext], WrappedNode]]:
    """Build a mapping-shaped custom formatter bounded by `max_dict`."""
    return _container_decorator(
        name=name,
        begin=begin,
        end=end,
        referable=referable,
        limit_option="max_dict",
    )


def _container_decorator[T](
    *,
    name: str | Text | None,
    begin: str | Text,
    end: str | Text,
    referable: bool,
    limit_option: str | None,
) -> Callable[[ItemProducer[T]], Callable[[T, PrettyContext], WrappedNode]]:
    begin_text = _punctuation(begin, "repr.tag_start")
    end_text = _punctuation(end, "repr.tag_end")

    def decorator(func: ItemProducer[T]) -> Callable[[T, PrettyContext], WrappedNode]:
        @functools.wraps(func)
        def wrapped(obj: T, ctx: PrettyContext) -> WrappedNode:
            limit = None if limit_option is None else getattr(ctx.options, limit_option)
            children = _collect_items(func(obj, ctx), ctx=ctx, limit=limit)
            return ctx.container(
                obj=obj,
                name=name,
                begin=begin_text,
                children=children,
                end=end_text,
                referable=referable,
            )

        return wrapped

    return decorator


def _collect_items(
    items: Iterable[WrappedItem | None],
    *,
    ctx: PrettyContext,
    limit: int | None,
) -> builtins.list[WrappedItem]:
    collected: builtins.list[WrappedItem] = []
    for item in items:
        if item is None:
            continue
        if not isinstance(item, WrappedItem):
            message = (
                f"custom pretty item must be WrappedItem, not {type(item).__name__}"
            )
            raise TypeError(message)
        if limit is not None and len(collected) >= limit:
            collected.append(ctx.ellipsis_item())
            break
        collected.append(item)
    return collected


def _punctuation(value: str | Text, style: str) -> Text:
    return value if isinstance(value, Text) else Text(value, style)


# These aliases intentionally match the concise public decorator vocabulary.
list = list_container  # noqa: A001
dict = dict_container  # noqa: A001

__all__ = ["container", "dict", "dict_container", "list", "list_container"]
