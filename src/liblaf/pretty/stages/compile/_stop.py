import enum

import attrs


class Flags(enum.Flag):
    NONE = 0
    NEWLINE = enum.auto()
    OVERFLOW = enum.auto()


@attrs.frozen
class PrettyCompileError(ValueError):
    flag: Flags
