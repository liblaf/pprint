from __future__ import annotations

from typing import ClassVar

import attrs


@attrs.frozen(kw_only=True)
class Flags:
    INLINE: ClassVar[Flags]
    BLOCK: ClassVar[Flags]
    multiline: bool
    break_before: bool = False
    break_after: bool = False


Flags.INLINE = Flags(multiline=False)
Flags.BLOCK = Flags(multiline=True, break_before=True, break_after=True)


@attrs.frozen(kw_only=True)
class Constraints:
    BLOCK: ClassVar[Constraints]
    INLINE: ClassVar[Constraints]
    KEY: ClassVar[Constraints]
    VALUE: ClassVar[Constraints]

    allow_multiline: bool = True
    allow_break_before: bool = True
    allow_break_after: bool = True

    def allow(self, flags: Flags) -> bool:
        return (
            (self.allow_multiline or not flags.multiline)
            and (self.allow_break_before or not flags.break_before)
            and (self.allow_break_after or not flags.break_after)
        )


Constraints.BLOCK = Constraints()
Constraints.INLINE = Constraints(
    allow_multiline=False, allow_break_before=False, allow_break_after=False
)
Constraints.KEY = Constraints(allow_break_after=False)
Constraints.VALUE = Constraints(allow_break_before=False)
