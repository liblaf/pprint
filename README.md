<div align="center" markdown>

![PPrint](https://socialify.git.ci/liblaf/pprint/image?description=1&forks=1&issues=1&language=1&name=1&owner=1&pattern=Transparent&pulls=1&stargazers=1&theme=Auto)

**[Explore the docs »](https://liblaf.github.io/pprint/)**

[![Codecov](https://codecov.io/gh/liblaf/pprint/graph/badge.svg)](https://codecov.io/gh/liblaf/pprint)
[![PyPI](https://img.shields.io/pypi/v/liblaf-pprint?logo=pypi&logoColor=white)](https://pypi.org/project/liblaf-pprint/)
[![Python](https://img.shields.io/pypi/pyversions/liblaf-pprint?logo=python&logoColor=white)](https://pypi.org/project/liblaf-pprint/)

[API Reference](https://liblaf.github.io/pprint/reference/liblaf/pprint/) · [Changelog](https://github.com/liblaf/pprint/blob/main/CHANGELOG.md) · [Report Bug](https://github.com/liblaf/pprint/issues)

![Rule](https://cdn.jsdelivr.net/gh/andreasbm/readme/assets/lines/rainbow.png)

</div>

`liblaf.pprint` formats Python values as compact plain text or width-aware Rich
renderables. It handles bounded containers, custom types, cycles, and shared
object identities without importing optional array frameworks.

## Installation

```bash
uv add liblaf-pprint
# or
pip install liblaf-pprint
```

## Quick start

```python
from rich.console import Console

from liblaf.pprint import pformat, render

value = {"answer": [1, 2, 3]}
assert pformat(value) == "{'answer': [1, 2, 3]}"
Console(width=12).print(render(value))
```

Use `pformat()` for text, `render()` for a Rich renderable, and `pprint()` (or
`pp()`) to print immediately. `plower()` remains available for integrations
that intentionally depend on the current lowered stage.

Custom formatters can be concise generators:

```python
from liblaf import pprint


class Point:
    @pprint.container()
    def __pretty__(self, ctx: pprint.Context):
        yield ctx.field("x", 1)
        yield ctx.field("y", 0, 0)


assert pprint.pformat(Point()) == "Point(x=1)"
```

Use `@pprint.list()` and `@pprint.dict()` for bounded list- and mapping-shaped
output. `register()` accepts both a type and a lazy `"module.Type"` target;
`register_func()` remains available for structural handlers.

## Traceback variables

`pformat_frames()` formats local-variable mappings from multiple frames in one
pass. It returns one tuple of `name = value` lines per input frame; the caller
retains ownership of filenames, source excerpts, and frame headings. References
therefore remain meaningful even when a value first appears in another frame.

```python
from liblaf.pprint import pformat_frames

shared = {"answer": 42}
frames = pformat_frames(({"payload": shared}, {"again": shared}))

assert frames[1] == ("again = <dict @ $frames[0].payload>",)
```

#### License

Copyright © 2026 [liblaf](https://github.com/liblaf). This project is
[MIT](https://spdx.org/licenses/MIT.html) licensed.
