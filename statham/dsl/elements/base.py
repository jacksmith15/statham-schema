# False positive. The cycle exists but is avoided by importing last.
# pylint: disable=cyclic-import
from collections import defaultdict
from typing import (
    Any,
    Callable,
    cast,
    DefaultDict,
    Dict,
    List,
    Generic,
    TypeVar,
    Union,
)

from statham.dsl.constants import NotPassed, Maybe
from statham.dsl.helpers import custom_repr
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
        # pylint: disable=invalid-name,redefined-builtin
        default: Maybe[Any] = NotPassed(),
        items: Maybe["Element"] = NotPassed(),
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
        additionalProperties: Union["Element", bool] = True,
    ):
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.default = default
        self.items = items
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

    def construct(self, value, _property):
        properties = getattr(self, "properties", NotPassed())
        additional_properties = getattr(
            self, "additionalProperties", NotPassed()
        )
        items = getattr(self, "items", NotPassed())
        return object_constructor(properties, additional_properties)(
            array_constructor(items)(value, _property)
        )

    def __call__(self, value, property_=None) -> Maybe[T]:
        """Validate and convert input data against the element.

        Runs validators defined on the `validators` property, and calls
        `construct` on the input.
        """
        property_ = property_ or UNBOUND_PROPERTY
        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            value = self.default
        for validator in self.validators:
            validator(value, property_)
        if isinstance(value, NotPassed):
            return value
        return self.construct(value, property_)


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
from statham.dsl.property import _Property, UNBOUND_PROPERTY


class _AnonymousObject(dict):
    """Anonymous object type.

    Allows dictionaries passed to untyped objects to use attribute access,
    to match `Object` instances.
    """

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        return self.__setitem__(key, value)


def object_constructor(
    properties: Maybe[Dict[str, _Property]] = NotPassed(),
    additional_properties: Maybe[Union[Element, bool]] = NotPassed(),
) -> Callable[[Any], _AnonymousObject]:
    """Recursively construct and validate sub-properties of object input."""
    # TODO: Use same `additional_properties` interface as on `Object`.
    default_prop: _Property = _Property(Element())
    if isinstance(additional_properties, Element):
        default_prop = _Property(additional_properties)
    default_properties: DefaultDict[str, _Property] = defaultdict(
        lambda: default_prop
    )
    if not isinstance(properties, NotPassed):
        default_properties.update(
            {prop.source or key: prop for key, prop in properties.items()}
        )

    def _constructor(value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        return _AnonymousObject(
            {
                default_properties[key].name
                or key: default_properties[key](sub_value)
                for key, sub_value in value.items()
            }
        )

    return _constructor


def array_constructor(
    items: Maybe[Element] = NotPassed()
) -> Callable[[Any, _Property], _AnonymousObject]:
    """Recursively construct and validate sub-properties of array input."""
    items_element: Element = Element()
    if isinstance(items, Element):
        items_element = items

    def _constructor(value: Any, property_: _Property) -> Any:
        if not isinstance(value, list):
            return value
        return [
            items_element(
                item, property_.evolve(property_.name or "" + f"[{idx}]")
            )
            for idx, item in enumerate(value)
        ]

    return _constructor
