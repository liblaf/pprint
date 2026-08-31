"""Helpers for tracking object identity across formatting stages."""

from typing import Self

import attrs


@attrs.frozen
class ObjectIdentifier:
    """Identity record used to detect shared and cyclic references.

    Attributes:
        cls: Runtime class of the referenced object, or `None` for a missing marker.
        id_: `id()` value for the referenced object, or `None` for a missing marker.
    """

    cls: type | None
    id_: int | None = attrs.field(alias="id")

    @classmethod
    def from_obj(cls, obj: object) -> Self:
        """Build an identifier from a concrete object.

        The formatter uses both `type(obj)` and `id(obj)` so later stages can
        produce readable fallback reference tags such as `<dict @ hexid>`.
        """
        return cls(cls=type(obj), id=id(obj))

    @classmethod
    def missing(cls) -> Self:
        """Build the sentinel identifier used for missing nodes."""
        return cls(cls=None, id=None)
