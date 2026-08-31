"""Base class for traced items."""

import abc
from typing import override

import attrs
from rich.text import Text

from liblaf.pprint.literals import EMPTY
from liblaf.pprint.stages.lowered import LoweredItem

from ._base import Traced
from ._context import LowerContext


@attrs.define
class TracedItem(Traced):
    """Base traced item that preserves prefix and suffix punctuation."""

    prefix: Text = attrs.field(default=EMPTY, kw_only=True)
    suffix: Text = attrs.field(default=EMPTY, kw_only=True)

    @override
    @abc.abstractmethod
    def lower(self, ctx: LowerContext) -> LoweredItem: ...
