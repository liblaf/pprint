from __future__ import annotations

import enum

from rich.segment import Segment
from rich.style import Style

TOKEN_META_KEY: str = "liblaf.pretty.token"  # noqa: S105


class Token(enum.Enum):
    COMMENT_BEGIN = enum.auto()
    COMMENT_END = enum.auto()

    @staticmethod
    def get_token(segment: Segment) -> Token | None:
        style: Style | None = segment.style
        if style is None:
            return None
        return style.meta.get(TOKEN_META_KEY)

    def match(self, segment: Segment) -> bool:
        return self.get_token(segment) is self

    def segment(self) -> Segment:
        style: Style = Style(meta={TOKEN_META_KEY: self})
        return Segment("", style=style)
