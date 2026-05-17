import abc
from collections.abc import Iterable, Sequence
from typing import Self

import attrs
from rich.text import Text


@attrs.frozen
class KeyEntry(abc.ABC):
    @abc.abstractmethod
    def __rich__(self) -> Text: ...


@attrs.frozen
class KeyPath:
    entries: Sequence[KeyEntry] = attrs.field(default=(), converter=tuple)

    def __add__(self, other: Iterable[KeyEntry]) -> Self:
        return type(self)((*self.entries, *other))

    def __rich__(self) -> Text:
        return Text.assemble(*[entry.__rich__() for entry in self.entries])


@attrs.frozen
class DictKey(KeyEntry):
    key: Text

    def __rich__(self) -> Text:
        return Text.assemble("[", self.key, "]")


@attrs.frozen
class DictKeyKey(KeyEntry):
    def __rich__(self) -> Text:
        return Text.assemble(
            ("<", "repr.tag_start"), ("key", "repr.tag_name"), (">", "repr.tag_end")
        )


@attrs.frozen
class DictValueKey(KeyEntry):
    def __rich__(self) -> Text:
        return Text()


@attrs.frozen
class GetAttrKey(KeyEntry):
    name: str

    def __rich__(self) -> Text:
        return Text.assemble(".", (self.name, "repr.attrib_name"))


@attrs.frozen
class SequenceKey(KeyEntry):
    index: int

    def __rich__(self) -> Text:
        return Text.assemble("[", (str(self.index), "repr.number"), "]")


@attrs.frozen
class VarKey(KeyEntry):
    name: str

    def __rich__(self) -> Text:
        return Text.assemble((self.name, "repr.attrib_name"))
