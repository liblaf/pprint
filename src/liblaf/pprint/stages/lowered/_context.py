"""Rendering helpers used while compiling lowered nodes into Rich segments."""

import contextlib
import functools
from collections.abc import Generator, Iterable

import attrs
import rich.segment
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.text import Text

type Renderable = RenderableType | Segment | None


class Segments(rich.segment.Segments):
    """Mutable segment collection with a cached display width."""

    segments: list[Segment]

    def __init__(
        self, segments: Iterable[Segment] | None = None, *, new_lines: bool = False
    ) -> None:
        if segments is None:
            segments: list[Segment] = []
        super().__init__(segments, new_lines=new_lines)

    @functools.cached_property
    def width(self) -> int:
        return sum(segment.cell_length for segment in self.segments)


def _default_console() -> Console:
    return Console(soft_wrap=True, markup=False, emoji=False, highlight=False)


@attrs.define
class CompileContext:
    """Stateful renderer used by lowered nodes and items.

    The context keeps track of the current output column, the active line
    prefix, and the Rich console options used to render nested text.
    """

    console: Console = attrs.field(factory=_default_console)
    column: int = attrs.field(default=0, kw_only=True)
    prefix: Segments = attrs.field(factory=Segments, kw_only=True)

    def _default_options(self) -> ConsoleOptions:
        return self.console.options.update(
            overflow="ignore", no_wrap=True, highlight=False, markup=False
        )

    _options: ConsoleOptions = attrs.field(
        default=attrs.Factory(_default_options, takes_self=True), alias="options"
    )

    @property
    def options(self) -> ConsoleOptions:
        return self._options.update(
            max_width=self._options.max_width - self.prefix.width
        )

    @property
    def remaining_width(self) -> int:
        return self._options.max_width - max(self.column, self.prefix.width)

    def ensure_newline(self) -> RenderResult:
        if self.column > 0:
            yield Segment.line()
            self.column = 0

    def render(self, *renderables: Renderable) -> RenderResult:
        segments: Segments = self._render(*renderables)
        for line_iterable, newline in Segment.split_lines_terminator(segments.segments):
            if self.column == 0:
                yield self.prefix
                if not newline:
                    self.column += self.prefix.width
            line: Segments = Segments(line_iterable)
            yield line
            if newline:
                yield Segment.line()
                self.column = 0
            else:
                self.column += line.width

    @contextlib.contextmanager
    def indent(self, indent: Renderable) -> Generator[None]:
        prefix_old: Segments = self.prefix
        self.prefix = self._render(self.prefix, indent)
        try:
            yield
        finally:
            self.prefix = prefix_old

    def _render(self, *renderables: Renderable) -> Segments:
        segments: list[Segment] = []
        for renderable in renderables:
            segments.extend(self._render_single(renderable))
        return Segments(segments)

    @functools.singledispatchmethod
    def _render_single(self, renderable: RenderableType) -> Iterable[Segment]:
        return self.console.render(renderable, options=self._options)

    @_render_single.register(str)
    def _render_single_str(self, renderable: str) -> Iterable[Segment]:
        return [Segment(renderable)]

    @_render_single.register(Segment)
    def _render_single_segment(self, renderable: Segment) -> Iterable[Segment]:
        return [renderable]

    @_render_single.register(Text)
    def _render_single_text(self, renderable: Text) -> Iterable[Segment]:
        renderable.overflow = "ignore"
        renderable.no_wrap = True
        renderable.end = ""
        return self.console.render(renderable, options=self._options)
