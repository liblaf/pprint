from __future__ import annotations

import sys
import types

from rich.text import Text

from liblaf.pprint.custom import PrettyContext, PrettyRegistry
from liblaf.pprint.stages.wrapped import WrappedLeaf, WrappedNode


def test_lazy_registration_waits_for_a_partially_imported_module() -> None:
    module_name = "_liblaf_pprint_test_lazy"
    module = types.ModuleType(module_name)
    registry = PrettyRegistry()
    sys.modules[module_name] = module
    try:

        @registry.register_lazy(module_name, "Target")
        def format_target(obj: object, ctx: PrettyContext) -> WrappedNode:
            return ctx.leaf(obj, Text("lazy"), referable=False)

        class Target:
            pass

        # A module can appear in sys.modules before its target class does.
        registry(Target(), PrettyContext(registry=registry))
        assert registry.lazy_handlers

        module.__dict__["Target"] = Target
        wrapped = registry(Target(), PrettyContext(registry=registry))

        assert isinstance(wrapped, WrappedLeaf)
        assert wrapped.value.plain == "lazy"
        assert not registry.lazy_handlers
    finally:
        del sys.modules[module_name]
