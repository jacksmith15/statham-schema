from typing import Any, Generic, TypeVar

from statham.dsl import validators as val
from statham.dsl.constants import NotPassed
from statham.dsl.elements.base import Element
from statham.dsl.helpers import custom_repr


T = TypeVar("T")


class _Property(Generic[T]):
    """Descriptor for a property on an object.

    Used to bind information about the enclosing object to a DSL Element,
    e.g. "required". Should be instantiated via `Property` to enable
    type inference on instances.
    """

    required: bool
    name: str
    parent: Any
    element: Element

    def __init__(self, element: Element[T], *, required: bool = False):
        self.element = element
        self.required = required

    def __eq__(self, other):
        if not isinstance(other, _Property):
            return False
        return self.element == other.element and self.required == other.required

    def evolve(self, name: str) -> "_Property":
        """Generate renamed property object to pass into nested elements."""
        property_: _Property[T] = _Property(
            element=self.element, required=self.required
        )
        property_.bind(self.parent, name)
        return property_

    def bind(self, parent: Any, name: str):
        self.parent = parent
        self.name = name

    def __call__(self, value):
        if not isinstance(self.element.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            value = self.element.default
        val.required(self.required)(self, value)
        return self.element(self, value)

    def __repr__(self):
        return custom_repr(self)

    @property
    def code(self):  # TODO: Move this code to the serializer.
        """Code representation uses the wrapping constructor `Property`."""
        return repr(self).replace(self.__class__.__name__, Property.__name__)

    @property
    def annotation(self):
        if self.required or not isinstance(
            getattr(self.element, "default"), NotPassed
        ):
            return self.element.annotation
        return f"Maybe[{self.element.annotation}]"


UNBOUND_PROPERTY: _Property = _Property(Element(), required=False)
UNBOUND_PROPERTY.bind(Element(), "<unbound>")


# Behaves as a wrapper for the `_Property` class.
# pylint: disable=invalid-name
def Property(element: Element, *, required: bool = False):
    """Wrapping constructor of `_Property`.

    This allows us to trick the type checker into interpreting instance
    attribute types of properties correctly.

    For example, the following becomes valid:
    ```python
    class Model(Object):
        string_value: str = Property(String(), required=True)
    ```

    See type stubs for this module for more detail.
    """
    return _Property(element, required=required)
