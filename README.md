<div align="center" markdown>

![PPrint](https://socialify.git.ci/liblaf/pprint/image?description=1&forks=1&issues=1&language=1&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)

**[Explore the docs »](https://liblaf.github.io/pprint/)**

[![Codecov](https://codecov.io/gh/liblaf/pprint/graph/badge.svg)](https://codecov.io/gh/liblaf/pprint)
[![PyPI](https://img.shields.io/pypi/v/liblaf-pprint?logo=pypi&logoColor=white)](https://pypi.org/project/liblaf-pprint/)
[![Python](https://img.shields.io/pypi/pyversions/liblaf-pprint?logo=python&logoColor=white)](https://pypi.org/project/liblaf-pprint/)

[API Reference](https://liblaf.github.io/pprint/reference/liblaf/pprint/) · [Changelog](https://github.com/liblaf/pprint/blob/main/CHANGELOG.md) · [Report Bug](https://github.com/liblaf/pprint/issues)

![Rule](https://cdn.jsdelivr.net/gh/andreasbm/readme/assets/lines/rainbow.png)

</div>

`liblaf.pprint` presents Python values for terminals, logs, and snapshots. Its
single entry point, `pretty()`, returns a stable Rich-capable `Pretty` object;
choose plain text with `.text()` or terminal output with `.show()`. It handles
bounded containers, custom types, cycles, and shared object identities without
importing optional array frameworks.

## Installation

```bash
uv add liblaf-pprint
# or
pip install liblaf-pprint
```

## Quick start

```python
from rich.console import Console

from liblaf.pprint import pretty

value = {"answer": [1, 2, 3]}
presentation = pretty(value)
assert presentation.text() == "{'answer': [1, 2, 3]}"
Console(width=12).print(presentation)
```

`Pretty` has one value-oriented interface across these destinations: pass it to
Rich for late-bound layout, use `.text(width=...)` for deterministic text, or
use `.show()` to write exactly one final newline. Its internal lowering stages
are not root API.

Custom formatters can be concise generators:

```python
from liblaf import pprint


class Point:
    @pprint.container()
    def __pretty__(self, ctx: pprint.Context):
        yield ctx.field("x", 1)
        yield ctx.field("y", 0, 0)


assert pprint.pretty(Point()).text() == "Point(x=1)"
```

Use `@pprint.list()` and `@pprint.dict()` for bounded list- and mapping-shaped
output. `register()` accepts both a type and a lazy `"module.Type"` target;
`register_func()` remains available for structural handlers.

## Traceback variables

`format_frame_variables()` is the batch seam for traceback renderers. It formats
local-variable mappings from multiple frames in one pass and returns one tuple
of `name = value` lines per input frame. The caller retains ownership of
filenames, source excerpts, and frame headings, while references remain
meaningful even when a value first appears in another frame.

```python
from liblaf.pprint import format_frame_variables

shared = {"answer": 42}
frames = format_frame_variables(({"payload": shared}, {"again": shared}))

assert frames[1] == ("again = <dict @ $frames[0].payload>",)
```

#### License

Copyright © 2026 [liblaf](https://github.com/liblaf). This project is
[MIT](https://spdx.org/licenses/MIT.html) licensed.
