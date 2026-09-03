from liblaf.pprint import format_frame_variables


def test_format_frame_variables_tracks_references_across_frame_variables() -> None:
    shared = {"answer": 42}

    frames = format_frame_variables(({"payload": shared}, {"again": shared}))

    assert frames == (
        ("payload = {'answer': 42}  # <dict @ $frames[0].payload>",),
        ("again = <dict @ $frames[0].payload>",),
    )


def test_format_frame_variables_preserves_frame_and_variable_order() -> None:
    frames = format_frame_variables(({"a": 1, "b": 2}, {"c": 3}))

    assert frames == (("a = 1", "b = 2"), ("c = 3",))


def test_format_frame_variables_formats_each_value_with_active_options() -> None:
    frames = format_frame_variables(({"items": [1, 2]},), max_list=1)

    assert frames == (("items = [1, ...]",),)
