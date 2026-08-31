"""Base class for traced nodes."""

import abc
from typing import override

import attrs

from liblaf.pprint.stages.lowered import LoweredNode

from ._base import Traced
from ._context import LowerContext


@attrs.define
class TracedNode(Traced):
    """Base traced node that lowers into a final renderable node."""

    @override
    @abc.abstractmethod
    def lower(self, ctx: LowerContext) -> LoweredNode: ...
