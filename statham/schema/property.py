from typing import Any, Dict, Generic, Optional, TypeVar, TYPE_CHECKING

from statham.schema.constants import NotPassed
from statham.schema.exceptions import SchemaDefinitionError
from statham.schema.helpers import custom_repr_args

if TYPE_CHECKING:
    from statham.schema.elements.base import Element  # pragma: no cover


PropType = TypeVar("PropType")


class _Property(Generic[PropType]):
    """Descriptor for a property on an object.

    Used to bind information about the enclosing object to a target Element,
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

    def clone(self):
        return _Property(
            self.element, required=self.required, source=self.source
        )

    def evolve(self, name: str) -> "_Property":
        """Generate renamed property object to pass into nested elements."""
        property_: _Property[PropType] = _Property(
            element=self.element, required=self.required, source=self.source
        )
        property_.bind(name=name, parent=self.parent)
        return property_

    def bind(self, name: str = None, parent: "Element" = None) -> None:
        if parent:
            self.parent = parent
        if not name:
            return
        if not self.source:
            self.source = name
        self.name = name

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
    :return: The property descriptor for this element.

    To hand property name conflicts, use the :paramref:`Property.source`
    option. For example, to express a property called `class`, one could
    do the following:

    .. code:: python

        class MyObject(Object):
            # Property called class
            class_: str = Property(String(), source="class")
    """
    return _Property(element, required=required, source=source)


class _PropertyDict(Dict[str, _Property[Any]]):
    """Container for properties.

    Used internally to bind properties to the enclosing element, and
    attribute name.
    """

    _parent: "Element"

    def __init__(self, *args, **kwargs):
        self._parent = None
        super().__init__(*args, **kwargs)
        bad_values = {
            name: prop
            for name, prop in self.items()  # pylint: disable=no-member
            if not isinstance(prop, _Property)
        }
        if bad_values:
            raise SchemaDefinitionError(f"Got bad property types: {bad_values}")

    def __setitem__(self, key, value):
        if not isinstance(value, _Property):
            raise SchemaDefinitionError(
                f"{key} must be a `Property`, got {value}"
            )
        super().__setitem__(key, value)  # pylint: disable=no-member
        value.bind(name=key, parent=self.parent)

    @property
    def parent(self) -> "Element":
        return self._parent

    @parent.setter
    def parent(self, value: "Element"):
        self._parent = value
        for key, prop in self.items():  # pylint: disable=no-member
            prop.bind(name=key, parent=value)

    @property
    def required(self):
        # pylint: disable=no-member
        return [
            prop.source or name
            for name, prop in self.items()
            if prop.required and isinstance(prop.element.default, NotPassed)
        ]
