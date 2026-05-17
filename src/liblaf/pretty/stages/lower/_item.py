import functools
from typing import Self, override

import attrs
from rich.text import Text

from liblaf.pretty.literals import EMPTY

from ._base import Layout, Lowered


@attrs.frozen
class LoweredItem(Lowered):
    wrapped: Lowered
    flat_gap: Text = attrs.field(default=EMPTY)

    @functools.cached_property
    @override
    def layouts(self) -> list[Layout]:
        raise ValueError

    @override
    def append(self, text: Text) -> Self:
        return attrs.evolve(self, wrapped=self.wrapped.append(text))
