# Depend only on `conf` within the liblaf package family

## Status

Accepted

## Decision

`liblaf.pprint` has a hard dependency on `liblaf.conf` for options and on Rich
for its current presentation adapter. It does not import sibling liblaf
packages. Type and functional registration remain one registry; `register()`
is only decorator sugar for type registration.

## Consequences

Traceback and logging can choose `liblaf.pprint` as an optional adapter without
creating an import cycle. A target-neutral document interface is deferred until
there is a second real presentation adapter.
