from typing import Any

from statham import validators as val
from statham.dsl.constants import NotPassed
from statham.dsl.elements.base import Element
from statham.dsl.helpers import custom_repr


class Property:
    """Descriptor for a property on an object."""

    required: bool
    name: str
    parent: Any
    element: Element

    def __init__(self, element: Element, *, required: bool = False):
        self.element = element
        self.required = required

    def evolve(self, name: str) -> "Property":
        """Generate renamed property object to pass into nested elements."""
        property_ = Property(element=self.element, required=self.required)
        property_.bind(self.parent, name)
        return property_

    def bind(self, parent: Any, name: str):
        self.parent = parent
        self.name = name

    def __call__(self, value):
        if not isinstance(self.element.default, NotPassed) and isinstance(
            value, NotPassed()
        ):
            value = self.element.default
        val.required(self.required)(self, value)
        return self.element(self, value)

    def __repr__(self):
        return custom_repr(self)


UNBOUND_PROPERTY = Property(Element(), required=False)
UNBOUND_PROPERTY.bind(Element(), "<unbound>")
