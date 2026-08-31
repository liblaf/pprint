import contextlib
import functools
from collections.abc import Generator, Iterable
from typing import Self

import attrs
from rich.console import Console, ConsoleOptions, RenderableType
from rich.containers import Renderables
from rich.segment import Segment
from rich.text import Text

from ._capture import Capture, CompileContextSnapshot, Compiled
from ._segments import Prefix


def _default_console() -> Console:
    return Console(soft_wrap=True, markup=False, emoji=False, highlight=False)


@attrs.define
class CompileContext:
    console: Console = attrs.field(factory=_default_console)
    prefix: Prefix = attrs.field(factory=Prefix, kw_only=True)

    def _default_options(self) -> ConsoleOptions:
        return self.console.options.update(
            overflow="ignore", no_wrap=True, highlight=False, markup=False
        )

    _options: ConsoleOptions = attrs.field(
        default=attrs.Factory(_default_options, takes_self=True), kw_only=True
    )

    captures: list[Capture] = attrs.field(factory=list)
    _column: int = attrs.field(default=0)

    @property
    def column(self) -> int:
        return self._column

    @column.setter
    def column(self, value: int) -> None:
        self._column = value
        if self._column > self._options.max_width:
            for capture in self.captures:
                capture.fits = False

    @property
    def options(self) -> ConsoleOptions:
        return self._options.update(
            max_width=max(self._options.max_width - self.prefix.width, 1)
        )

    def capture(self) -> Capture:
        return Capture(context=self)

    def clone(self) -> Self:
        return attrs.evolve(self, captures=[])

    def commit(self, compiled: Compiled) -> None:
        self._extend_segments(compiled)
        if not compiled.fits:
            self._overflow()
        self.column = compiled.context.column
        self.console = compiled.context.console
        self._options = compiled.context.options
        self.prefix = compiled.context.prefix

    @contextlib.contextmanager
    def indent(self, indent: Text) -> Generator[None]:
        prefix_old: Prefix = self.prefix
        self.prefix = Prefix(self._render(self.prefix, indent))
        try:
            yield
        finally:
            self.prefix = prefix_old

    def newline(self) -> None:
        self._append_segment(Segment.line())
        self.column = 0

    def preview(self, *renderables: RenderableType) -> Compiled:
        ctx: Self = self.clone()
        with ctx.capture() as capture:
            ctx.print(*renderables)
        return capture.get()

    def print(self, *renderables: RenderableType) -> None:
        for line, newline in Segment.split_lines_terminator(self._render(*renderables)):
            if self.column == 0:
                self._extend_segments(self.prefix)
                self.column += self.prefix.width
            self._extend_segments(line)
            self.column += sum(segment.cell_length for segment in line)
            if newline:
                self.newline()

    def snapshot(self) -> CompileContextSnapshot:
        return CompileContextSnapshot(
            column=self.column,
            console=self.console,
            options=self._options,
            prefix=self.prefix,
        )

    def _append_segment(self, segment: Segment) -> None:
        for capture in self.captures:
            capture.data.append(segment)

    def _extend_segments(self, segments: Iterable[Segment]) -> None:
        for capture in self.captures:
            capture.data.extend(segments)

    def _overflow(self) -> None:
        for capture in self.captures:
            capture.fits = False

    def _render(self, *renderables: RenderableType) -> Iterable[Segment]:
        renderables: list[RenderableType] = [
            _patch_renderable(renderable) for renderable in renderables
        ]
        return self.console.render(Renderables(renderables), options=self.options)


@functools.singledispatch
def _patch_renderable(renderable: RenderableType) -> RenderableType:
    return renderable


@_patch_renderable.register
def _(renderable: str) -> Text:
    return Text(renderable, overflow="ignore", no_wrap=True, end="")


@_patch_renderable.register
def _(renderable: Text) -> Text:
    renderable: Text = renderable.copy()
    renderable.overflow = "ignore"
    renderable.no_wrap = True
    renderable.end = ""
    return renderable
