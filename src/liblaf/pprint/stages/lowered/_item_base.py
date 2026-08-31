"""Shared base class for lowered items inside a container."""

import abc
import functools

import attrs
from rich.text import Text

from liblaf.pprint.literals import EMPTY

from ._base import Lowered


@attrs.frozen
class LoweredItem(Lowered):
    """Base class for lowered items that carry prefix and suffix text."""

    prefix: Text = attrs.field(default=EMPTY, kw_only=True)
    suffix: Text = attrs.field(default=EMPTY, kw_only=True)

    @functools.cached_property
    @abc.abstractmethod
    def width_inline(self) -> int | None: ...
