"""Fallback repr-based formatting helpers.

When no custom handler matches, `liblaf.pprint` falls back to `reprlib` for
size-aware repr output and then runs Rich's repr highlighter over the result.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.highlighter import ReprHighlighter
from rich.text import Text

from liblaf.pprint.stages.wrapped import WrappedLeaf

if TYPE_CHECKING:
    from ._context import PrettyContext

_HIGHLIGHTER: ReprHighlighter = ReprHighlighter()


def pretty_repr(obj: Any, ctx: PrettyContext, *, referable: bool = True) -> WrappedLeaf:
    """Format `obj` with `reprlib` and Rich's repr highlighter.

    The active repr limits come from [`PrettyContext.arepr`][liblaf.pprint.custom.PrettyContext.arepr].
    """
    raw: str = ctx.arepr.repr1(obj, ctx.arepr.maxlevel - ctx.depth)
    text: Text = _HIGHLIGHTER(raw)
    return ctx.leaf(obj, text, referable=referable)
