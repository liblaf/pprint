"""Shared state used while lowering traced nodes."""

import attrs


@attrs.frozen
class LowerContext:
    """Lowering context that resolves stable display names for types."""

    typenames: dict[type, str]
    max_reference_path: int

    def get_ref_typename(self, cls: type) -> str:
        """Return the short name used inside `<Type @ path>` reference tags."""
        return self.typenames.get(cls) or cls.__name__

    def get_tag_typename(self, cls: type) -> str:
        """Return the tag name used at the front of rendered containers."""
        return self.typenames.get(cls, cls.__name__)
