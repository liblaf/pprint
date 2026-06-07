import attrs

from ._flags import Effects, StopReason
from ._segment import MutableSegments, Segments
from ._token import Token


@attrs.frozen
class Compiled(Segments):
    flags: StopReason = StopReason.NONE
    stop: StopReason = StopReason.NONE

    @property
    def effects(self) -> Effects:
        return Effects(
            begin_break=self.begin_break,
            end_break=self.end_break,
            multiline=self.multiline,
            fits=self.fits,
        )

    @property
    def begin_break(self) -> bool:
        if not self.data:
            return False
        return Token.COMMENT_BEGIN.match(self.data[0])

    @property
    def end_break(self) -> bool:
        if not self.data:
            return False
        return Token.COMMENT_END.match(self.data[-1])

    @property
    def fits(self) -> bool:
        return StopReason.OVERFLOW not in self.flags

    @property
    def multiline(self) -> bool:
        return StopReason.NEWLINE in self.flags


@attrs.define
class Capture(MutableSegments):
    flags: StopReason = StopReason.NONE
    stop: StopReason = StopReason.NONE

    def get(self) -> Compiled:
        return Compiled(self.data, flags=self.flags, stop=self.stop)
