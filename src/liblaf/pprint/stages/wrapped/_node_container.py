"""Wrapped repr-like containers."""

from collections.abc import Generator, Iterable
from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.stages.traced import TracedContainer, TracedNode

from ._base import WrappedChild
from ._context import TraceContext
from ._item_base import WrappedItem
from ._item_positional import WrappedPositionalItem
from ._node_object import WrappedObject


@attrs.define
class WrappedContainer(WrappedObject):
    """Wrapped container that enqueues child items for breadth-first tracing."""

    begin: Text
    children: Iterable[WrappedItem]
    end: Text
    indent: Text
    name: Text | None = attrs.field(default=None, kw_only=True)

    def _default_empty(self) -> Text:
        return self.begin + self.end

    empty: Text = attrs.field(
        default=attrs.Factory(_default_empty, takes_self=True), kw_only=True
    )

    def iter_children(
        self, ctx: TraceContext, traced: TracedContainer
    ) -> Generator[WrappedChild]:
        for i, child in enumerate(self.children):
            if ctx.depth >= ctx.options.max_level:
                yield WrappedChild(
                    wrapped=WrappedPositionalItem.ellipsis(),
                    depth=ctx.depth + 1,
                    attach=traced.children.append,  # ty:ignore[invalid-argument-type]
                    path=ctx.path,
                )
                break
            if isinstance(child, WrappedPositionalItem) and not child.path_segment:
                child.path_segment = f"[{i}]"
            yield WrappedChild(
                wrapped=child,
                depth=ctx.depth + 1,
                attach=traced.children.append,  # ty:ignore[invalid-argument-type]
                path=ctx.path,
            )

    @override
    def trace(self, ctx: TraceContext) -> tuple[Iterable[WrappedChild], TracedNode]:
        if (ref := self.visit(ctx)) is not None:
            return (), ref
        traced = TracedContainer(
            begin=self.begin,
            children=[],
            end=self.end,
            indent=self.indent,
            name=self.name,
            empty=self.empty,
            identifier=self.identifier,
            path=ctx.path,
        )
        if self.identifier.id_ is not None:
            ctx.trace_cache[self.identifier.id_] = traced
        return self.iter_children(ctx, traced), traced
