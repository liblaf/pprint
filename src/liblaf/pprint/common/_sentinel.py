import enum
from typing import Any


class TruncatedType(enum.Enum):
    TRUNCATED = enum.auto()


TRUNCATED: Any = TruncatedType.TRUNCATED
