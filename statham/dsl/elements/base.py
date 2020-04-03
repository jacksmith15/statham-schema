# False positive. The cycle exists but is avoided by importing last.
# pylint: disable=cyclic-import
from typing import Any, cast, Dict, List, Generic, TypeVar, Union

from statham.dsl.constants import NotPassed, Maybe
from statham.dsl.exceptions import ValidationError
from statham.dsl.helpers import custom_repr
from statham.dsl.property import _Property
from statham.dsl.validation import (
    get_validators,
    InstanceOf,
    NoMatch,
    Validator,
)


T = TypeVar("T")

Numeric = Union[int, float]


# This emulates the options available to a general JSONSchema object.
# pylint: disable=too-many-instance-attributes
class Element(Generic[T]):
    """Schema element for composing instantiation logic.

    The generic type is bound by subclasses to indicate their return
    type when called.
    # TODO: enum
    # TODO: const
    # TODO: composition?
    """

    # This is how many options there are!
    # pylint: disable=too-many-locals
    def __init__(
        self,
        *,
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        default: Maybe[Any] = NotPassed(),
        items: Maybe[Union["Element", List["Element"]]] = NotPassed(),
        additionalItems: Union["Element", bool] = True,
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
        minimum: Maybe[Numeric] = NotPassed(),
        maximum: Maybe[Numeric] = NotPassed(),
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
        format: Maybe[str] = NotPassed(),
        pattern: Maybe[str] = NotPassed(),
        minLength: Maybe[int] = NotPassed(),
        maxLength: Maybe[int] = NotPassed(),
        required: Maybe[List[str]] = NotPassed(),
        properties: Maybe[Dict[str, "_Property"]] = NotPassed(),
        patternProperties: Maybe[Dict[str, "Element"]] = NotPassed(),
        additionalProperties: Union["Element", bool] = True,
    ):
        self.default = default
        self.items = items
        self.additionalItems = additionalItems
        self.minItems = minItems
        self.maxItems = maxItems
        self.minimum = minimum
        self.maximum = maximum
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf
        self.format = format
        self.pattern = pattern
        self.minLength = minLength
        self.maxLength = maxLength
        self.required = required
        self.properties = properties
        if isinstance(self.properties, dict):
            for name, prop in (self.properties or {}).items():
                prop.bind_class(type(self))
                prop.bind_name(name)
                if prop.required:
                    self.required = list(
                        set(cast(List[str], self.required or []) + [name])
                    )
        self.patternProperties = patternProperties
        self.additionalProperties = additionalProperties

    def __repr__(self):
        """Dynamically construct the repr to match value instantiation."""
        return custom_repr(self)

    def __eq__(self, other):
        """Check if two elements are equivalent.

        This just checks the type and public attribute values. Useful for
        testing parser logic, and could be used to automatically DRY up
        messy schemas in future.
        """
        if not isinstance(other, self.__class__):
            return False
        pub_vars = lambda x: {
            k: v for k, v in vars(x).items() if not k.startswith("_")
        }
        return pub_vars(self) == pub_vars(other)

    @property
    def annotation(self) -> str:
        generic = type(self).__orig_bases__[0].__args__[0]  # type: ignore
        if isinstance(generic, TypeVar):  # type: ignore
            return "Any"
        return generic.__name__

    @property
    def type_validator(self) -> Validator:
        return InstanceOf()

    @property
    def validators(self) -> List[Validator]:
        validators: List[Validator] = [self.type_validator] + list(
            get_validators(self)
        )
        return validators

    def construct(self, value, property_):
        if isinstance(value, list):
            return self.__items__(value, property_)
        if isinstance(value, dict):
            return _AnonymousObject(**self.__properties__(value))
        return value

    @property
    def __properties__(self) -> "Properties":
        return Properties(
            self,
            getattr(self, "properties", NotPassed()),
            getattr(self, "patternProperties", NotPassed()),
            getattr(self, "additionalProperties", True),
        )

    @property
    def __items__(self) -> "Items":
        return Items(
            getattr(self, "items", NotPassed()),
            getattr(self, "additionalItems", True),
        )

    def __call__(self, value, property_=None) -> Maybe[T]:
        """Validate and convert input data against the element.

        Runs validators defined on the `validators` property, and calls
        `construct` on the input.
        """
        property_ = property_ or UNBOUND_PROPERTY

        def create(value):
            for validator in self.validators:
                validator(value, property_)
            return self.construct(value, property_)

        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            try:
                return create(self.default)
            except (TypeError, ValidationError):
                return self.default
        if isinstance(value, NotPassed):
            return value
        return create(value)


UNBOUND_PROPERTY: _Property = _Property(Element(), required=False)
UNBOUND_PROPERTY.bind_name("<unbound>")
UNBOUND_PROPERTY.bind_class(Element())


class Nothing(Element):
    """Element which matches nothing. Equivalent to False."""

    def __init__(self):
        super().__init__()  # Don't allow args to Nothing.

    def __bool__(self):
        return False

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def validators(self) -> List[Validator]:
        return [NoMatch()]


# Needs to be imported last to prevent cyclic import.
# pylint: disable=wrong-import-position
from statham.dsl.elements.properties import Properties
from statham.dsl.elements.items import Items


class _AnonymousObject(dict):
    """Anonymous object type.

    Allows dictionaries passed to untyped objects to use attribute access,
    to match `Object` instances.
    """

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        return self.__setitem__(key, value)
