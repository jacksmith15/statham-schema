from typing import Any, Generic, Optional, TypeVar, TYPE_CHECKING

from statham.dsl.constants import NotPassed
from statham.dsl.helpers import custom_repr_args

if TYPE_CHECKING:
    from statham.dsl.elements.base import Element  # pragma: no cover


PropType = TypeVar("PropType")


class _Property(Generic[PropType]):
    """Descriptor for a property on an object.

    Used to bind information about the enclosing object to a DSL Element,
    e.g. "required". Should be instantiated via `Property` to enable
    type inference on instances.
    """

    required: bool
    parent: Any
    element: "Element"
    source: Optional[str]
    name: Optional[str]

    def __init__(
        self,
        element: "Element[PropType]",
        *,
        required: bool = False,
        source: str = None,
    ):
        self.element = element
        self.required = required
        self.name: Optional[str] = None
        self.source: Optional[str] = source
        self.parent = None

    def __eq__(self, other):
        if not isinstance(other, _Property):
            return False
        return (
            self.element == other.element
            and self.required == other.required
            and self.source == other.source
        )

    def evolve(self, name: str) -> "_Property":
        """Generate renamed property object to pass into nested elements."""
        property_: _Property[PropType] = _Property(
            element=self.element, required=self.required, source=self.source
        )
        property_.bind_name(name)
        property_.bind_class(self.parent)
        return property_

    def bind_name(self, name: str):
        if not self.source:
            self.source = name
        self.name = name

    def bind_class(self, parent: Any):
        self.parent = parent

    def __call__(self, value):
        return self.element(value, self)

    def __repr__(self):
        repr_args = custom_repr_args(self)
        if self.source == self.name:
            _ = repr_args.kwargs.pop("source", None)
        return f"{self.__class__.__name__.lstrip('_')}{repr(repr_args)}"

    @property
    def annotation(self):
        if self.required or not isinstance(
            getattr(self.element, "default", NotPassed()), NotPassed
        ):
            return self.element.annotation
        return f"Maybe[{self.element.annotation}]"

    def python(self) -> str:
        prop_def = repr(self)
        return (
            (f"{self.name}: {self.annotation} = {prop_def}")
            if self.name
            else prop_def
        )


# Behaves as a wrapper for the `_Property` class.
# pylint: disable=invalid-name
def Property(element: "Element", *, required: bool = False, source: str = None):
    """Descriptor for adding a property when declaring an object schema model.

    Return value is typed to inform instance-level interface (see type stubs).

    :param element: The JSON Schema Element object accepted by this property.
    :param required: Whether this property is required. If false, then this
        field may be omitted when data is passed to the outer object's
        constructor.
    :param source: The source name of this property. Only necessary if it must
        differ from that of the attribute.

    To hand property name conflicts, use the :paramref:`Property.source`
    option. For example, to express a property called `class`, one could
    do the following:

    .. code:: python

        class MyObject(Object):
            # Property called class
            class_: str = Property(String(), source="class")
    """
    return _Property(element, required=required, source=source)
