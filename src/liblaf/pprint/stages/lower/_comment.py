from __future__ import annotations

import enum
from collections.abc import Sequence

from rich.text import Text


class CommentLayout(enum.Enum):
    NONE = enum.auto()
    AFTER = enum.auto()
    BEFORE = enum.auto()

    @classmethod
    def filter_layouts(cls, comment: Text | None) -> Sequence[CommentLayout]:
        return (cls.AFTER, cls.BEFORE) if comment else (cls.NONE,)
