"""Lazy wrapper that defers actual wrapping until tracing needs it."""

from collections.abc import Callable, Iterable
from typing import override

import attrs

from liblaf.pprint.stages.traced import TracedNode

from ._base import WrappedChild
from ._context import TraceContext
from ._node_base import WrappedNode


@attrs.define
class WrappedLazy(WrappedNode):
    """Placeholder node that memoizes the wrapped result on first use."""

    factory: Callable[[], WrappedNode]
    _cache: WrappedNode | None = attrs.field(default=None, init=False)

    @override
    def trace(self, ctx: TraceContext) -> tuple[Iterable[WrappedChild], TracedNode]:
        if self._cache is None:
            self._cache = self.factory()
        return self._cache.trace(ctx)
