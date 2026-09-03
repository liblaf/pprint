"""Readable Python-value presentations for terminals, logs, and snapshots.

Use [`pretty`][liblaf.pprint.pretty] to construct a
[`Pretty`][liblaf.pprint.Pretty] presentation, then hand it to Rich, capture
plain text with `.text()`, or emit it with `.show()`.
"""

from lazy_loader import attach_stub

__getattr__, __dir__, __all__ = attach_stub(__name__, __file__)

del attach_stub
