"""Shared base class for lowered scalar and container nodes."""

import abc
import functools

import attrs
from rich.console import RenderResult
from rich.text import Text

from liblaf.pprint.literals import EMPTY

from ._base import Lowered
from ._context import CompileContext


@attrs.frozen
class LoweredNode(Lowered):
    """Base class for lowered nodes with optional reference annotations."""

    annotation: Text = attrs.field(default=EMPTY, kw_only=True)

    @abc.abstractmethod
    def render_flat(
        self, ctx: CompileContext, *, annotation: bool = False
    ) -> RenderResult: ...

    @abc.abstractmethod
    def render_break(
        self, ctx: CompileContext, *, annotation: bool = True
    ) -> RenderResult: ...

    @functools.cached_property
    @abc.abstractmethod
    def width_break_begin(self) -> int | None: ...

    @functools.cached_property
    @abc.abstractmethod
    def width_break_end(self) -> int | None: ...

    @functools.cached_property
    @abc.abstractmethod
    def width_flat(self) -> int | None: ...
