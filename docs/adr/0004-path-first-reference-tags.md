# Prefer anchor paths in shared-reference tags

## Status

Accepted

## Decision

The first breadth-first occurrence of a referable object is its anchor.
Subsequent occurrences, including cycles, render that anchor's `$`-rooted path
in both the reference tag and the anchor annotation. When the path exceeds the
configured `max_other` character budget, both locations use the object's
hexadecimal identity instead.

## Consequences

Common output points at a location a reader can find directly, while deep or
wide structures retain a bounded inline tag. The formatting pass remains
single-pass and does not attempt width-dependent re-anchoring.
