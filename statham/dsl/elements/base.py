# False positive. The cycle exists but is avoided by importing last.
# pylint: disable=cyclic-import
from typing import Any, Callable, List, Generic, TypeVar, Union

from statham.dsl.constants import NotPassed, Maybe
from statham.dsl.helpers import custom_repr
from statham.dsl.validators import SCHEMA_ATTRIBUTE_VALIDATORS


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
    # TODO: type-specific keywords don't apply to element.
    """

    default: Any = NotPassed()

    def __init__(
        self,
        *,
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        default: Maybe[str] = NotPassed(),
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
        minimum: Maybe[Numeric] = NotPassed(),
        maximum: Maybe[Numeric] = NotPassed(),
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        format: Maybe[str] = NotPassed(),
        # pylint: enable=redefined-builtin
        pattern: Maybe[str] = NotPassed(),
        minLength: Maybe[int] = NotPassed(),
        maxLength: Maybe[int] = NotPassed(),
    ):
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.default = default
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
        return "Any"

    @property
    def type_validator(self):
        return lambda _, __: None

    @property
    def validators(self) -> List[Callable]:
        validators = [self.type_validator]
        for key, value in vars(self).items():
            validator = SCHEMA_ATTRIBUTE_VALIDATORS.get(key)
            if validator and value != NotPassed():
                validators.append(validator(value))
        return validators

    # Default implementation doesn't need self.
    # pylint: disable=no-self-use
    def construct(self, value, _property):
        return value

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


# Needs to be imported last to prevent cyclic import.
# pylint: disable=wrong-import-position
from statham.dsl.property import UNBOUND_PROPERTY
