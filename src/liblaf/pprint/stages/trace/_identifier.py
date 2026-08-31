import attrs

from ._key import KeyPath


@attrs.frozen
class Identifier:
    cls: type | None = None
    id_: int | None = None
    path: KeyPath = attrs.field(default=KeyPath())
