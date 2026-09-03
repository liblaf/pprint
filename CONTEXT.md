# Pretty Printing

This context describes the language used to turn Python values into readable,
width-aware presentations.

## Language

**Value**:
The Python object supplied to one formatting pass.
_Avoid_: Item, input

**Formatting pass**:
One complete interpretation of a value using a single resolved option set.
_Avoid_: Render, print

**Pretty**:
A stable presentation of one value that can be rendered by Rich, captured as
plain text, or shown on a console.
_Avoid_: Lowered node, formatter result

**Reference**:
A later occurrence of a referable value whose shallowest first occurrence
is its anchor.
_Avoid_: Duplicate, copy

**Custom formatter**:
A value-specific rule that describes a presentation using the public document
vocabulary.
_Avoid_: Repr override, renderer

**Frame-variable batch**:
An ordered sequence of frame-local mappings formatted with one shared reference
graph, while the caller owns frame labels and source presentation.
_Avoid_: Stack trace, traceback renderer
