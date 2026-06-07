from __future__ import annotations

import contextlib
from collections.abc import Generator, Iterable
from typing import Self

import attrs
import rich
from rich.console import Console, ConsoleOptions, RenderableType
from rich.containers import Renderables
from rich.segment import Segment

from ._capture import Capture, Compiled
from ._flags import PrettyCompileError, StopReason
from ._segment import Segments


@attrs.define
class CompileContext:
    def _default_console() -> Console:
        return rich.get_console()

    def _default_options(self) -> ConsoleOptions:
        return self.console.options.update(
            overflow="ignore", no_wrap=True, highlight=False, markup=False
        )

    console: Console = attrs.field(factory=_default_console)
    _capture: Capture = attrs.field(factory=Capture, repr=False)
    _column: int = 0
    _options: ConsoleOptions = attrs.field(
        default=attrs.Factory(_default_options, takes_self=True)
    )
    _prefix: Segments = attrs.field(factory=Segments)
    _stop: StopReason = StopReason.NONE

    @property
    def options(self) -> ConsoleOptions:
        width: int = max(self.console.width - max(self._column, self._prefix.width), 1)
        return self._options.update_width(width)

    @contextlib.contextmanager
    def capture(self, *, stop: StopReason | None = None) -> Generator[Capture]:
        capture: Capture = Capture()
        saved: dict[str, object] = attrs.asdict(self, recurse=False)
        self._capture = capture
        if stop is not None:
            self._stop = stop
        try:
            yield capture
        except PrettyCompileError as err:
            capture.stop = err.flag
        finally:
            for key, value in saved.items():
                setattr(self, key, value)

    @contextlib.contextmanager
    def indent(self, *indent: RenderableType) -> Generator[Self]:
        saved: Segments = self._prefix
        self._prefix = Segments(
            self._render(self._prefix, *indent, options=self._options)
        )
        try:
            yield self
        finally:
            self._prefix = saved

    def newline(self) -> None:
        self._capture.append(Segment.line())
        self._column = 0
        self._set_flag(StopReason.NEWLINE)

    def print(self, *renderables: RenderableType) -> None:
        segments: Iterable[Segment] = self._render(*renderables)
        for line, newline in Segment.split_lines_terminator(segments):
            if self._column == 0:
                self._capture += self._prefix
                self._column += self._prefix.width
            self._capture += line
            self._column += sum(segment.cell_length for segment in line)
            if self._column > self._options.max_width:
                self._set_flag(StopReason.OVERFLOW)
            if newline:
                self.newline()

    def render(
        self, *renderables: RenderableType, stop: StopReason | None = None
    ) -> Compiled:
        with self.capture(stop=stop) as capture:
            self.print(*renderables)
        return capture.get()

    def _render(
        self, *renderables: RenderableType, options: ConsoleOptions | None = None
    ) -> Iterable[Segment]:
        if options is None:
            options = self.options
        return self.console.render(Renderables(renderables), options)

    def _set_flag(self, flag: StopReason) -> None:
        self._capture.flags |= flag
        if flag in self._stop:
            raise PrettyCompileError(flag)
