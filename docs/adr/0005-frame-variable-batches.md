# Trace frame variables as one batch

## Status

Accepted

## Decision

`pformat_frames()` accepts ordered frame-local mappings and performs one shared
wrap-and-trace pass, returning only grouped `name = value` lines. Its reference
paths start at `$frames[frame-index].variable`; traceback code remains
responsible for frame headings, locations, and source excerpts.

## Consequences

Repeated identities remain deduplicated across frames without coupling pprint
to traceback presentation. The grouped string result is intentionally plain,
so width-aware frame layout is not part of this package's public contract.
