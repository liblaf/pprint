import enum

from rich.segment import Segment
from rich.style import Style

TOKEN_META_KEY: str = "liblaf.pretty.token"  # noqa: S105


class Token(enum.Enum):
    HARD_BREAK = enum.auto()

    def segment(self) -> Segment:
        style: Style = Style(meta={TOKEN_META_KEY: self})
        return Segment("", style=style)
