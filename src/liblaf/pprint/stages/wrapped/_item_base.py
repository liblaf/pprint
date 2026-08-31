"""Base class for wrapped items."""

import abc
from collections.abc import Iterable
from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.literals import EMPTY
from liblaf.pprint.stages.traced import TracedItem

from ._base import Wrapped, WrappedChild
from ._context import TraceContext


@attrs.define
class WrappedItem(Wrapped):
    """Base wrapped item that stores prefix and suffix punctuation."""

    prefix: Text = attrs.field(default=EMPTY, kw_only=True)
    suffix: Text = attrs.field(default=EMPTY, kw_only=True)
    path_segment: str = attrs.field(default="", init=False)

    @override
    @abc.abstractmethod
    def trace(self, ctx: TraceContext) -> tuple[Iterable[WrappedChild], TracedItem]: ...
