"""Customization helpers for teaching `liblaf.pprint` new formatting rules.

Import [`PrettyContext`][liblaf.pprint.custom.PrettyContext] together with
[`register_type`][liblaf.pprint.custom.register_type],
[`register_func`][liblaf.pprint.custom.register_func], or
[`register_lazy`][liblaf.pprint.custom.register_lazy] when you want to format a
new kind of object. Importing this module also loads the built-in handlers for
core containers, optional array summaries, `fieldz`-compatible models, and
`__rich_repr__` objects.
"""

from ._context import PrettyContext
from ._decorators import container, dict, list  # noqa: A004

# register prelude handlers
from ._prelude import _array, _container, _fieldz, _scalar  # noqa: F401
from ._registry import (
    PrettyHandler,
    PrettyRegistry,
    register,
    register_func,
    register_lazy,
    register_type,
    registry,
)

Context = PrettyContext

__all__ = [
    "Context",
    "PrettyContext",
    "PrettyHandler",
    "PrettyRegistry",
    "container",
    "dict",
    "list",
    "register",
    "register_func",
    "register_lazy",
    "register_type",
    "registry",
]
