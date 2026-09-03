from __future__ import annotations

import sys
import types
from collections.abc import Iterator

from liblaf import pprint
from liblaf.pprint.stages.wrapped import WrappedItem, WrappedNode


def test_container_decorator_and_context_item_vocabulary() -> None:
    class Point:
        def __init__(self) -> None:
            self.x = 1
            self.y = 2

        @pprint.container()
        def __pretty__(self, ctx: pprint.Context) -> Iterator[WrappedItem | None]:
            yield ctx.field("x", self.x)
            yield ctx.field("y", self.y, 2)

    class Alias:
        @pprint.container(name="Named")
        def __pretty__(self, ctx: pprint.Context) -> Iterator[WrappedItem | None]:
            yield ctx.item(0, "value")
            yield ctx.key_value("answer", 42)

    assert pprint.pretty(Point()).text() == "Point(x=1)"
    assert pprint.pretty(Alias()).text() == "Named('value', 'answer': 42)"


def test_list_and_dict_decorators_use_their_option_limits() -> None:
    class Sequence:
        @pprint.list()
        def __pretty__(self, ctx: pprint.Context) -> Iterator[WrappedItem | None]:
            for index in range(3):
                yield ctx.item(index, index)

    class Mapping:
        @pprint.dict()
        def __pretty__(self, ctx: pprint.Context) -> Iterator[WrappedItem | None]:
            for index in range(3):
                yield ctx.key_value(index, index)

    assert pprint.pretty(Sequence(), max_list=1).text() == "Sequence[0, ...]"
    assert pprint.pretty(Mapping(), max_dict=1).text() == "Mapping{0: 0, ...}"


def test_container_uses_item_indexes_and_referable_spelling() -> None:
    child = {"answer": 42}

    class Indexed:
        @pprint.container(referable=False)
        def __pretty__(self, ctx: pprint.Context) -> Iterator[WrappedItem | None]:
            yield ctx.item(7, child)
            yield ctx.item(8, child)

    output = pprint.pretty(Indexed()).text()

    assert "# <Indexed" not in output
    assert "<dict @ $[7]>" in output


def test_register_accepts_lazy_module_type_syntax() -> None:
    module_name = "_liblaf_pprint_register_string"
    module = types.ModuleType(module_name)

    class Target:
        pass

    module.__dict__["Target"] = Target
    sys.modules[module_name] = module
    try:

        @pprint.register(f"{module_name}.Target")
        def format_target(obj: Target, ctx: pprint.Context) -> WrappedNode:
            return ctx.leaf(obj, pprint.literals.ELLIPSIS, referable=False)

        assert pprint.pretty(Target()).text() == "..."
    finally:
        del sys.modules[module_name]
