from typing import Any, Generic, Type, TypeVar

from statham.dsl.constants import Maybe
from statham.dsl.elements.base import Element


T = TypeVar("T")


class _Property(Generic[T]):
    """Descriptor for a property on an object."""

    required: bool
    name: str
    parent: Any
    element: Element[T]

    def __init__(self, element: Element[T], *, required: bool = False):
        ...

    def evolve(self, name: str) -> "_Property":
        ...

    def bind(self, parent: Any, name: str) -> None:
        ...

    def __call__(self, value: Any) -> Maybe[T]:
        ...

    def __repr__(self) -> str:
        ...


UNBOUND_PROPERTY: _Property


# Let the instance attributes have the enclosed type of the element.
# TODO: Support literal types of Python 3.8 to vary return type between
#   `T` and `Maybe[T]`
def Property(element: Element[T], *, required: bool = False) -> T:
    ...
