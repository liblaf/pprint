# References and identities

`liblaf.pprint` follows object identity during one formatting pass. The first
breadth-first appearance of a referable value is its anchor; later appearances
become `<Type @ path>` references. This prevents cycles from expanding forever
and makes shared values visible in logs and tracebacks.

Paths start at `$` for `pretty()` and at `$frames` for
`format_frame_variables()`.
If an anchor path would exceed `max_other`, the formatter uses the object's
hexadecimal identity instead, keeping the reference itself bounded.

Scalars and built-in lists and tuples are deliberately not referable. Custom
containers are referable by default; use `referable=False` when a formatter is
only an inline summary and should render every time.
