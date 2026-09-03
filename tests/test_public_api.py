from __future__ import annotations

import re

import pytest
import rich
from rich.console import Console
from rich.text import Text

import liblaf.pprint as pprint_module
from liblaf.pprint import Pretty, pretty, register
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


def test_pretty_is_the_public_presentation_boundary() -> None:
    value = {"answer": [1, 2, 3]}

    presentation = pretty(value)

    assert isinstance(presentation, Pretty)
    assert presentation.text() == "{'answer': [1, 2, 3]}"
    assert capture(presentation) == "{'answer': [1, 2, 3]}"


def test_root_exports_presentation_not_compatibility_or_pipeline_helpers() -> None:
    for name in ("pformat", "render", "pprint", "pp", "plower", "stages"):
        assert name not in pprint_module.__all__


def test_show_writes_exactly_one_final_newline() -> None:
    console = Console(file=None, color_system=None, width=88)
    with console.capture() as result:
        assert pretty([1, 2]).show(console=console) is None
        assert pretty([3, 4]).show(console=console) is None

    assert result.get() == "[1, 2]\n[3, 4]\n"


def test_show_uses_the_active_rich_console(monkeypatch: pytest.MonkeyPatch) -> None:
    console = Console(file=None, color_system=None, width=88)
    monkeypatch.setattr(rich, "get_console", lambda: console)

    with console.capture() as result:
        pretty([1, 2]).show()

    assert result.get() == "[1, 2]\n"


def test_text_rejects_nonpositive_width() -> None:
    with pytest.raises(AssertionError):
        pretty([1, 2]).text(width=0)


def test_repeated_identity_anchors_shallowest_occurrence_with_path_reference() -> None:
    child = {"x": 1}
    output = pretty({"left": child, "right": child}).text()

    assert output.index("'left'") < output.index("'right'")
    assert "'left': {'x': 1},  # <dict @ $['left']>" in output
    assert "'right': <dict @ $['left']>" in output


def test_cycle_uses_the_anchor_path_without_recursive_expansion() -> None:
    value: list[object] = []
    value.append(value)

    assert pretty(value).text() == "[<list @ $>]  # <list @ $>"


def test_long_anchor_path_falls_back_to_hex_identity() -> None:
    child = {"x": 1}

    output = pretty({"a very long key": child, "again": child}, max_other=8).text()

    assert re.search(r"'a very long key': \{'x': 1\},  # <dict @ [0-9a-f]+>", output)
    assert re.search(r"'again': <dict @ [0-9a-f]+>", output)


def test_pretty_defers_layout_to_rich_and_text_accepts_explicit_width() -> None:
    value = {"alpha": [1, 2, 3]}
    presentation = pretty(value)

    assert "\n" not in capture(presentation, width=88).rstrip("\n")
    assert "\n" in capture(presentation, width=12).rstrip("\n")
    assert presentation.text(width=88) == "{'alpha': [1, 2, 3]}"
    assert "\n" in presentation.text(width=12)


def test_register_is_type_registration_sugar() -> None:
    class Point:
        pass

    @register(Point)
    def format_point(obj: Point, ctx: PrettyContext) -> WrappedNode:
        return ctx.leaf(obj, Text("point"), referable=False)

    assert pretty(Point()).text() == "point"


def test_short_arrays_keep_repr_and_long_arrays_use_summary() -> None:
    np = __import__("numpy")

    assert pretty(np.arange(3), max_array=5).text() == "array([0, 1, 2])"
    assert pretty(np.arange(5), max_array=5).text() == "i64[5](numpy)"
