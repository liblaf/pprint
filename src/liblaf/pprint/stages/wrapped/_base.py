"""Wrapped values used before tracing references."""

from __future__ import annotations

import abc
from collections.abc import Callable, Iterable
from typing import NamedTuple

import attrs

from liblaf.pprint.stages.traced import Traced

from ._context import TraceContext


class WrappedChild(NamedTuple):
    """Queued child plus the callback that should receive its traced result."""

    wrapped: Wrapped
    depth: int
    attach: Callable[[Traced], None]
    path: str


@attrs.define
class Wrapped(abc.ABC):
    """Interface implemented by wrapped nodes and items."""

    @abc.abstractmethod
    def trace(self, ctx: TraceContext) -> tuple[Iterable[WrappedChild], Traced]: ...
