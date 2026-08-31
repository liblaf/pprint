"""Lazy summaries for optional array and tensor libraries."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from rich.text import Text

from liblaf.pprint.custom._context import PrettyContext
from liblaf.pprint.custom._registry import registry
from liblaf.pprint.stages.wrapped import WrappedNode

if TYPE_CHECKING:
    import jax
    import numpy as np
    import torch
    import warp as wp


@registry.register_lazy("jax", "Array")
def _pretty_jax_array(obj: jax.Array, ctx: PrettyContext) -> WrappedNode | None:
    return _array_summary(obj, ctx, str(obj.dtype), obj.shape, "jax", obj.device)


@registry.register_lazy("numpy", "ndarray")
def _pretty_numpy_array(obj: np.ndarray, ctx: PrettyContext) -> WrappedNode | None:
    return _array_summary(obj, ctx, str(obj.dtype), obj.shape, "numpy")


@registry.register_lazy("torch", "Tensor")
def _pretty_torch_tensor(obj: torch.Tensor, ctx: PrettyContext) -> WrappedNode | None:
    return _array_summary(obj, ctx, str(obj.dtype), obj.shape, "torch", obj.device)


@registry.register_lazy("warp", "array")
def _pretty_warp_array(obj: wp.array, ctx: PrettyContext) -> WrappedNode | None:
    return _array_summary(obj, ctx, str(obj.dtype), obj.shape, "warp", obj.device)


def _array_summary(
    obj: Any,
    ctx: PrettyContext,
    dtype: str,
    shape: Sequence[int],
    module: str,
    device: object | None = None,
) -> WrappedNode | None:
    """Return a compact dtype-and-shape summary for a long array.

    Arrays whose every dimension is shorter than `max_array` decline this
    handler so their normal repr remains visible.
    """
    if all(d < ctx.options.max_array for d in shape):
        return None
    dtype = dtype.rsplit(".", maxsplit=1)[-1]
    dtype = (
        dtype.replace("float", "f")
        .replace("uint", "u")
        .replace("int", "i")
        .replace("complex", "c")
    )
    metadata: list[str] = [module]
    if device is not None:
        metadata.append(str(device))
    return ctx.leaf(
        obj,
        Text.assemble(
            dtype,
            ("[", "repr.brace"),
            Text(",", "repr.comma").join(Text(str(d), "repr.number") for d in shape),
            ("]", "repr.brace"),
            "(",
            ", ".join(metadata),
            ")",
        ),
    )
