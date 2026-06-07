import enum
from collections.abc import Generator

import attrs


class StopReason(enum.Flag):
    NONE = 0
    NEWLINE = enum.auto()
    OVERFLOW = enum.auto()
    SYNTAX_ERROR = enum.auto()


@attrs.frozen
class PrettyCompileError(ValueError):
    flag: StopReason


@attrs.frozen
class Constraints:
    begin_break: bool | None = None
    end_break: bool | None = None
    multiline: bool | None = None

    def iter_fields(self) -> Generator[tuple[str, bool]]:
        for field in attrs.fields(type(self)):
            value: bool | None = getattr(self, field.name)
            if value is not None:
                yield field.name, value


@attrs.frozen
class Effects:
    begin_break: bool
    end_break: bool
    multiline: bool
    fits: bool

    def conflict(self, constraints: Constraints) -> bool:
        for name, constraint in constraints.iter_fields():
            effect: bool = getattr(self, name)
            if effect != constraint:
                return True
        return False

    def satisfy(self, constraints: Constraints) -> bool:
        for name, constraint in constraints.iter_fields():
            effect: bool = getattr(self, name)
            if effect != constraint:
                return False
        return True


@attrs.frozen
class Hints:
    begin_break: bool | None = None
    end_break: bool | None = None
    multiline: bool | None = None

    def conflict(self, constraints: Constraints) -> bool:
        for name, constraint in constraints.iter_fields():
            hint: bool | None = getattr(self, name)
            if hint is not None and hint != constraint:
                return True
        return False
