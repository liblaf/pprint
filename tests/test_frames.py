from liblaf.pprint import pformat_frames


def test_pformat_frames_tracks_references_across_frame_variables() -> None:
    shared = {"answer": 42}

    frames = pformat_frames(({"payload": shared}, {"again": shared}))

    assert frames == (
        ("payload = {'answer': 42}  # <dict @ $frames[0].payload>",),
        ("again = <dict @ $frames[0].payload>",),
    )


def test_pformat_frames_preserves_frame_and_variable_order() -> None:
    frames = pformat_frames(({"a": 1, "b": 2}, {"c": 3}))

    assert frames == (("a = 1", "b = 2"), ("c = 3",))


def test_pformat_frames_formats_each_value_with_the_active_options() -> None:
    frames = pformat_frames(({"items": [1, 2]},), max_list=1)

    assert frames == (("items = [1, ...]",),)
