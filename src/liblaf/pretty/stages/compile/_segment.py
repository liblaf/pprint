import functools
from collections.abc import Iterable, MutableSequence, Sequence
from typing import overload, override

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

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Sequence[Segment]:
        return self.data

    @functools.cached_property
    def width(self) -> int:
        return sum(segment.cell_length for segment in self.data)


@attrs.define
class MutableSegments(MutableSequence[Segment]):
    data: list[Segment] = attrs.field(factory=list)

    @overload
    def __getitem__(self, index: int, /) -> Segment: ...
    @overload
    def __getitem__(self, index: slice[int | None], /) -> MutableSequence[Segment]: ...
    @override
    def __getitem__(
        self, index: int | slice[int | None]
    ) -> Segment | MutableSequence[Segment]:
        return self.data[index]

    @overload
    def __setitem__(self, index: int, value: Segment, /) -> None: ...
    @overload
    def __setitem__(
        self, index: slice[int | None], value: Iterable[Segment], /
    ) -> None: ...
    @override
    def __setitem__(
        self, index: int | slice[int | None], value: Segment | Iterable[Segment]
    ) -> None:
        self.data[index] = value  # pyrefly: ignore [unsupported-operation]

    @overload
    def __delitem__(self, index: int, /) -> None: ...
    @overload
    def __delitem__(self, index: slice[int | None], /) -> None: ...
    @override
    def __delitem__(self, index: int | slice[int | None]) -> None:
        del self.data[index]

    @override
    def __len__(self) -> int:
        return len(self.data)

    @override
    def insert(self, index: int, value: Segment) -> None:
        self.data.insert(index, value)
