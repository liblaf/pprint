"""Configuration types and environment-backed defaults for `liblaf.pprint`.

`liblaf.pprint` supports both per-call overrides and `PPRINT_*` environment
variables. This module defines the public override surface and the normalized
options object used during a single formatting pass.
"""

from typing import ClassVar, TypedDict

import attrs
from rich.text import Text

from liblaf import conf
from liblaf.pprint.literals import INDENT


class PrettyOverrides(TypedDict, total=False):
    """Keyword overrides accepted by the public formatting functions.

    Attributes:
        max_level: Maximum nesting depth before values collapse to `...`.
        max_list: Maximum visible items for list-like containers.
        max_array: Maximum elements forwarded to repr-style array handlers.
        max_dict: Maximum visible key-value pairs for mappings.
        max_string: Maximum string repr length before truncation.
        max_long: Maximum integer repr length before truncation.
        max_other: Maximum repr length for other scalar values.
        indent: Indentation used when layouts wrap across lines. String values
            may be plain text, Rich markup, or ANSI-colored text.
        hide_defaults: Hide default-valued fields from `fieldz` and `__rich_repr__`
            output.
    """

    hide_defaults: bool
    indent: str | Text
    max_array: int
    max_dict: int
    max_level: int
    max_list: int
    max_long: int
    max_other: int
    max_string: int


def _as_text(value: str | Text) -> Text:
    """Normalize string-like indentation into Rich text.

    Plain strings are treated as Rich markup. ANSI escapes are preserved by
    routing them through [`Text.from_ansi`][rich.text.Text.from_ansi].
    """
    if isinstance(value, Text):
        return value
    if "\x1b" in value:
        return Text.from_ansi(value)
    return Text.from_markup(value)


@attrs.frozen
class PrettyOptions:
    """Resolved options for a single formatting pass.

    These values are usually created from [`config`][liblaf.pprint.config] plus
    per-call [`PrettyOverrides`][liblaf.pprint.PrettyOverrides].

    Attributes:
        max_level: Maximum nesting depth before values collapse to `...`.
        max_list: Maximum visible items for list-like containers.
        max_array: Maximum elements forwarded to repr-style array handlers.
        max_dict: Maximum visible key-value pairs for mappings.
        max_string: Maximum string repr length before truncation.
        max_long: Maximum integer repr length before truncation.
        max_other: Maximum repr length for other scalar values.
        indent: Indentation used when layouts wrap across lines, normalized to
            [`Text`][rich.text.Text].
        hide_defaults: Hide default-valued fields from `fieldz` and `__rich_repr__`
            output.
    """

    hide_defaults: bool
    indent: Text = attrs.field(converter=_as_text)
    max_array: int
    max_dict: int
    max_level: int
    max_list: int
    max_long: int
    max_other: int
    max_string: int


def field_text(*, default: Text) -> conf.Field[Text]:
    """Create a config field that accepts markup, ANSI, or Rich text.

    This is used by [`PrettyConfig`][liblaf.pprint.PrettyConfig] for the public
    `indent` option.
    """
    return conf.field(default=default, converter=_as_text)


class PrettyConfig(conf.BaseConfig):
    """Environment-backed defaults for the pretty printer.

    Values are loaded from `PPRINT_*` variables and can be overridden per call with
    [`pretty`][liblaf.pprint.pretty]. `PPRINT_INDENT` accepts the same markup
    and ANSI inputs as the per-call `indent` override.
    """

    env_prefix: ClassVar[str] = "PPRINT_"

    hide_defaults: conf.Field[bool] = conf.field_bool(default=True)
    indent: conf.Field[Text] = field_text(default=INDENT)
    max_array: conf.Field[int] = conf.field_int(default=5)
    max_dict: conf.Field[int] = conf.field_int(default=4)
    max_level: conf.Field[int] = conf.field_int(default=6)
    max_list: conf.Field[int] = conf.field_int(default=6)
    max_long: conf.Field[int] = conf.field_int(default=40)
    max_other: conf.Field[int] = conf.field_int(default=30)
    max_string: conf.Field[int] = conf.field_int(default=30)

    def dump(self) -> PrettyOptions:
        """Materialize the current configuration as [`PrettyOptions`][liblaf.pprint.PrettyOptions].

        The returned object is a snapshot of the current environment-backed
        values, with `indent` normalized to [`Text`][rich.text.Text].
        """
        return PrettyOptions(**self.to_dict())


config: PrettyConfig = PrettyConfig()
