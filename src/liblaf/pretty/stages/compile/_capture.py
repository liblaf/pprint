import attrs
from rich.style import Style

from ._segment import MutableSegments, Segments
from ._stop import Flags
from ._token import TOKEN_META_KEY, Token


@attrs.frozen
class Compiled(Segments):
    flags: Flags = Flags.NONE
    stop: Flags = Flags.NONE

    @property
    def begin_break(self) -> bool:
        if not self.data:
            return False
        style: Style | None = self.data[0].style
        if style is None:
            return False
        return style.meta.get(TOKEN_META_KEY, None) is Token.HARD_BREAK

    @property
    def end_break(self) -> bool:
        if not self.data:
            return False
        style: Style | None = self.data[-1].style
        if style is None:
            return False
        return style.meta.get(TOKEN_META_KEY, None) is Token.HARD_BREAK

    @property
    def fits(self) -> bool:
        return Flags.OVERFLOW not in self.flags

    @property
    def is_multiline(self) -> bool:
        return Flags.NEWLINE in self.flags


@attrs.define
class Capture(MutableSegments):
    flags: Flags = Flags.NONE
    stop: Flags = Flags.NONE

    def get(self) -> Compiled:
        return Compiled(self.data, flags=self.flags, stop=self.stop)
