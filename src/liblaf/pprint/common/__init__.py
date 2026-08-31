"""Shared sentinels and identity helpers used by the formatting pipeline.

Most extensions only need this module indirectly through
[`PrettyContext`][liblaf.pprint.custom.PrettyContext]. Reach for
[`ObjectIdentifier`][liblaf.pprint.common.ObjectIdentifier] when you are
working on the pipeline itself, or [`TRUNCATED`][liblaf.pprint.common.TRUNCATED]
when you need to detect internal truncation markers.
"""

from lazy_loader import attach_stub

__getattr__, __dir__, __all__ = attach_stub(__name__, __file__)

del attach_stub
