import attrs
from rich.text import Text

from ._identifier import Identifier


@attrs.frozen
class LowerContext:
    def get_ref_typename(self, cls: type) -> str:
        raise NotImplementedError

    def get_tag_typename(self, cls: type | None) -> str:
        raise NotImplementedError

    def make_comment(self, identifier: Identifier) -> Text:
        assert identifier.cls is not None
        return Text(
            f"# <{self.get_ref_typename(identifier.cls)} @ {identifier.path.__rich__().plain}>",
            "dim",
        )
