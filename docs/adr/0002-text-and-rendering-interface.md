# Keep text and Rich rendering as separate interfaces

## Status

Accepted

## Decision

`pformat()` returns plain text, `render()` returns a Rich renderable, and
`pprint()`/`pp()` write to a console. `plower()` remains an advanced interface
for callers that knowingly depend on the current lowered pipeline.

## Consequences

Callers that need snapshots, logs, or serialization do not acquire a console
dependency. Rich console width remains late-bound for interactive output.
