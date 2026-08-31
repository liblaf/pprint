"""Registration machinery for custom pretty-printers.

This module exposes the registry object and the decorators that most users
import from [`liblaf.pprint.custom`][liblaf.pprint.custom].
"""

from __future__ import annotations

import functools
import sys
import types
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, NamedTuple, Protocol, overload

import attrs

from liblaf.pprint.stages.wrapped import WrappedNode

from ._repr import pretty_repr

if TYPE_CHECKING:
    from ._context import PrettyContext


class PrettyHandler[T](Protocol):
    """Protocol implemented by pretty-printer callbacks.

    Handlers receive the object plus the active
    [`PrettyContext`][liblaf.pprint.custom.PrettyContext] and either return a
    wrapped node or `None` to decline.
    """

    def __call__(self, obj: T, ctx: PrettyContext, /) -> WrappedNode | None: ...


class _LazyType(NamedTuple):
    module: str
    name: str


def _default_type_dispatcher() -> functools._SingleDispatchCallable[WrappedNode | None]:
    @functools.singledispatch
    def type_dispatcher(obj: Any, ctx: PrettyContext) -> WrappedNode | None:
        del obj, ctx
        return None

    return type_dispatcher


@attrs.define
class PrettyRegistry:
    """Ordered registry of custom pretty-printer handlers.

    Resolution prefers an object's `__pretty__` method, then registered type-based
    handlers, then registered functional handlers, and finally falls back to
    repr-based formatting.

    Attributes:
        handlers: Structural handlers checked in reverse registration order.
        lazy_handlers: Deferred registrations waiting for an optional dependency
            to appear in `sys.modules`.
        type_dispatcher: `singledispatch`-backed dispatcher for concrete types.
    """

    handlers: list[PrettyHandler[Any]] = attrs.field(factory=list)
    lazy_handlers: dict[_LazyType, PrettyHandler[Any]] = attrs.field(factory=dict)
    type_dispatcher: functools._SingleDispatchCallable[WrappedNode | None] = (
        attrs.field(factory=_default_type_dispatcher)
    )

    def __call__(self, obj: Any, ctx: PrettyContext) -> WrappedNode:
        """Wrap `obj` with the first matching registered handler.

        Returning `None` from `__pretty__` or a structural handler lets the
        registry continue searching for another match.
        """
        if (pretty := getattr(obj, "__pretty__", None)) is not None and (
            wrapped := pretty(ctx)
        ) is not None:
            return wrapped
        self.resolve_lazy()
        if (wrapped := self.type_dispatcher(obj, ctx)) is not None:
            return wrapped
        for handler in reversed(self.handlers):
            if (wrapped := handler(obj, ctx)) is not None:
                return wrapped
        return pretty_repr(obj, ctx)

    def register_func[F: PrettyHandler[Any]](self, func: F) -> F:
        """Register a structural handler.

        Functional handlers run after type-based handlers. Later registrations win
        because the registry checks them in reverse order.
        """
        self.handlers.append(func)
        return func

    @overload
    def register_lazy[F: PrettyHandler[Any]](
        self, module: str, name: str, func: F
    ) -> F: ...
    @overload
    def register_lazy[F: PrettyHandler[Any]](
        self, module: str, name: str, func: None = None
    ) -> Callable[[F], F]: ...
    def register_lazy[F: PrettyHandler[Any]](
        self, module: str, name: str, func: F | None = None
    ) -> Callable[..., Any]:
        """Register a handler for a type that may come from an optional dependency.

        The registry does not import `module` for you. Instead, the handler becomes
        active once that module is already present in `sys.modules`.
        """
        if func is None:
            return functools.partial(self.register_lazy, module, name)
        self.lazy_handlers[_LazyType(module, name)] = func
        return func

    @overload
    def register_type[F: PrettyHandler[Any]](self, cls: type, func: F) -> F: ...
    @overload
    def register_type[F: PrettyHandler[Any]](
        self, cls: type, func: None = None
    ) -> Callable[[F], F]: ...
    def register_type[F: PrettyHandler[Any]](
        self, cls: type, func: F | None = None
    ) -> Callable[..., Any]:
        """Register a handler for `cls` and its subclasses."""
        if func is None:
            return functools.partial(self.register_type, cls)
        return self.type_dispatcher.register(cls, func)

    def resolve_lazy(self) -> None:
        """Resolve pending lazy registrations against already imported modules.

        Once a lazy target resolves, it is promoted into the normal type
        dispatcher for future lookups.
        """
        for (module_name, cls_name), handler in list(self.lazy_handlers.items()):
            module: types.ModuleType | None = sys.modules.get(module_name)
            if module is None:
                continue
            cls: object | None = getattr(module, cls_name, None)
            if cls is None:
                # Modules can be visible while they are still initializing. Keep
                # the registration inspectable and retry on a later formatting pass.
                continue
            if not isinstance(cls, type):
                msg = (
                    f"lazy pretty target {module_name}.{cls_name} must be a type, "
                    f"not {type(cls).__name__}"
                )
                raise TypeError(msg)
            self.register_type(cls, handler)
            del self.lazy_handlers[_LazyType(module_name, cls_name)]


registry: PrettyRegistry = PrettyRegistry()
register_func = registry.register_func
register_lazy = registry.register_lazy
register_type = registry.register_type


@overload
def register[F: PrettyHandler[Any]](target: type | str, func: F) -> F: ...


@overload
def register[F: PrettyHandler[Any]](
    target: type | str, func: None = None
) -> Callable[[F], F]: ...


def register[F: PrettyHandler[Any]](
    target: type | str, func: F | None = None
) -> F | Callable[[F], F]:
    """Register a concrete type or a lazy ``"module.Type"`` target."""
    if isinstance(target, str):
        module, separator, name = target.rpartition(".")
        if not separator:
            message = "lazy pretty targets must use 'module.Type' syntax"
            raise ValueError(message)
        return registry.register_lazy(module, name, func)
    if not isinstance(target, type):
        message = f"pretty target must be a type or string, not {type(target).__name__}"
        raise TypeError(message)
    return registry.register_type(target, func)
