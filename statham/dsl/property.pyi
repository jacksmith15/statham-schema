from typing import Any, Generic, Type, TypeVar

from statham.dsl.constants import Maybe
from statham.dsl.elements.base import Element


PropType = TypeVar("PropType")


class _Property(Generic[PropType]):
    """Descriptor for a property on an object."""

    required: bool
    name: str
    parent: Any
    element: Element[PropType]

    def __init__(
        self,
        element: Element[PropType],
        *,
        required: bool = False,
        name: str = None
    ):
        ...

    def evolve(self, name: str) -> "_Property":
        ...

    def bind_name(self, name: str) -> None:
        ...

    def bind_class(self, parent: Any) -> None:
        ...

    @property
    def annotation(self) -> str:
        ...

    def __call__(self, value: Any) -> Maybe[PropType]:
        ...

    def __repr__(self) -> str:
        ...


UNBOUND_PROPERTY: _Property


# Let the instance attributes have the enclosed type of the element.
# TODO: Can we use literal types of Python 3.8 to vary return type between
#   `T` and `Maybe[T]`?
def Property(
    element: Element[PropType],
    required: bool = False,
    name: str = None
) -> PropType:
    ...
