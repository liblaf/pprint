import functools
from collections.abc import Iterable, Sequence
from typing import Self, overload, override

import attrs
from rich.console import Console, ConsoleOptions
from rich.segment import Segment


@attrs.frozen
class Segments(Sequence[Segment]):
    data: Sequence[Segment] = attrs.field(default=(), converter=tuple)

    @overload
    def __getitem__(self, index: int, /) -> Segment: ...
    @overload
    def __getitem__(self, index: slice[int | None], /) -> Sequence[Segment]: ...
    @override
    def __getitem__(
        self, index: int | slice[int | None]
    ) -> Segment | Sequence[Segment]:
        return self.data[index]

    @override
    def __len__(self) -> int:
        return len(self.data)

    def __add__(self, other: Iterable[Segment]) -> Self:
        return type(self)([*self.data, *other])

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Sequence[Segment]:
        return self.data


@attrs.frozen
class Prefix(Segments):
    @functools.cached_property
    def width(self) -> int:
        assert not any("\n" in segment.text for segment in self.data)
        return sum(segment.cell_length for segment in self.data)
