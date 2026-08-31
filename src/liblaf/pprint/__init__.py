"""Public API for `liblaf.pprint`.

Import [`pformat`][liblaf.pprint.pformat] when you want plain text,
[`plower`][liblaf.pprint.plower] when you want the width-aware Rich renderable,
[`pprint`][liblaf.pprint.pprint] or [`pp`][liblaf.pprint.pp] when you want to
print immediately, and the registration helpers when you need to teach the
formatter about custom types.
"""

from lazy_loader import attach_stub

__getattr__, __dir__, __all__ = attach_stub(__name__, __file__)

del attach_stub
