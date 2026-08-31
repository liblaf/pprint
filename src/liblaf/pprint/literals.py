"""Styled Rich text fragments reused throughout the formatter."""

from rich.text import Text

COLON: Text = Text.assemble((":", "repr.colon"), " ")
COMMA: Text = Text(",", "repr.comma")
COMMENT_GAP: Text = Text("  ", "repr.comment")
ELLIPSIS: Text = Text("...", "repr.ellipsis")
EMPTY: Text = Text()
EQUAL: Text = Text("=", "repr.attrib_equal")
INDENT: Text = Text("|   ", "repr.indent")
SPACE: Text = Text(" ")
