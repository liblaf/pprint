from __future__ import annotations

import re

from rich.console import Console
from rich.text import Text

from liblaf.pprint import pformat, plower, pp, pprint, register, render
from liblaf.pprint.custom import PrettyContext
from liblaf.pprint.stages.wrapped import WrappedNode


def capture(value: object, *, width: int = 88) -> str:
    console = Console(
        color_system=None,
        force_terminal=False,
        highlight=False,
        markup=False,
        width=width,
    )
    with console.capture() as result:
        console.print(value)
    return result.get()


def test_public_formatting_contracts() -> None:
    value = {"answer": [1, 2, 3]}

    assert pformat(value) == "{'answer': [1, 2, 3]}"
    assert capture(render(value)) == "{'answer': [1, 2, 3]}"
    assert plower(value).to_plain() == pformat(value)


def test_pprint_and_pp_write_to_given_console() -> None:
    console = Console(file=None, color_system=None, width=88)
    with console.capture() as result:
        assert pprint([1, 2], console=console) is None
        assert pp([3, 4], console=console) is None

    assert result.get() == "[1, 2]\n[3, 4]\n"


def test_repeated_identity_anchors_shallowest_occurrence_with_path_reference() -> None:
    child = {"x": 1}
    output = pformat({"left": child, "right": child})

    assert output.index("'left'") < output.index("'right'")
    assert "'left': {'x': 1},  # <dict @ $['left']>" in output
    assert "'right': <dict @ $['left']>" in output


def test_cycle_uses_the_anchor_path_without_recursive_expansion() -> None:
    value: list[object] = []
    value.append(value)

    assert pformat(value) == "[<list @ $>]  # <list @ $>"


def test_long_anchor_path_falls_back_to_hex_identity() -> None:
    child = {"x": 1}

    output = pformat({"a very long key": child, "again": child}, max_other=8)

    assert re.search(r"'a very long key': \{'x': 1\},  # <dict @ [0-9a-f]+>", output)
    assert re.search(r"'again': <dict @ [0-9a-f]+>", output)


def test_render_defers_layout_to_console_width() -> None:
    value = {"alpha": [1, 2, 3]}

    assert "\n" not in capture(render(value), width=88).rstrip("\n")
    assert "\n" in capture(render(value), width=12).rstrip("\n")


def test_register_is_type_registration_sugar() -> None:
    class Point:
        pass

    @register(Point)
    def format_point(obj: Point, ctx: PrettyContext) -> WrappedNode:
        return ctx.leaf(obj, Text("point"), referable=False)

    assert pformat(Point()) == "point"


def test_short_arrays_keep_repr_and_long_arrays_use_summary() -> None:
    np = __import__("numpy")

    assert pformat(np.arange(3), max_array=5) == "array([0, 1, 2])"
    assert pformat(np.arange(5), max_array=5) == "i64[5](numpy)"
