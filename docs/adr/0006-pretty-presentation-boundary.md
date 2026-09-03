# Use `Pretty` as the presentation boundary

## Status

Accepted; supersedes [ADR 0002](0002-text-and-rendering-interface.md) and
[ADR 0005](0005-frame-variable-batches.md).

## Decision

`pretty(value, **overrides)` constructs a stable `Pretty` presentation. `Pretty`
implements Rich's render protocol, `.text(width=88)` returns deterministic
plain text, and `.show(console=None)` emits the presentation with one final
newline. The internal lowered node and pipeline stages are not root API.
`format_frame_variables()` is the explicitly named batch integration seam for
traceback-style frame locals: it traces ordered mappings through one shared
reference graph and returns grouped plain-text `name = value` lines while the
caller owns frame presentation.

## Consequences

One object represents one value across Rich terminals, logs, and snapshots,
without making callers select a compatibility-shaped entry point first.
Integrators migrate from `pformat_frames()` to `format_frame_variables()`;
ordinary callers migrate former text, render, and print helpers to the matching
`Pretty` capability.
