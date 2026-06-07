import attrs


class _Base:
    begin_break: bool | None = None
    end_break: bool | None = None
    multiline: bool | None = None


@attrs.frozen
class Constraints(_Base): ...


@attrs.frozen
class FlagsHint(_Base): ...
