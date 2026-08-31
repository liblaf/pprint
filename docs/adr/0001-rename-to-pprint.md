# Rename the distribution and import package to `pprint`

## Status

Accepted

## Decision

The project distribution is `liblaf-pprint`, the import package is
`liblaf.pprint`, and project URLs use the `pprint` repository name. The source
tree and documentation references move with Git history rather than being
copied. `PPRINT_*` is the environment-variable prefix.

## Consequences

This is a deliberate breaking rename from `liblaf-pretty` and
`liblaf.pretty`. A compatibility import package would retain a second public
module and hide incomplete migration work, so it is not provided.
