from typing import Any, Callable, List, Generic, TypeVar

from statham.dsl.constants import NotPassed, Maybe
from statham.dsl.helpers import custom_repr


T = TypeVar("T")


class Element(Generic[T]):
    """Schema element for composing instantiation logic.

    The generic type is bound by subclasses to indicate their return
    type when called.
    """

    default: Any

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
        return [self.type_validator]

    # Default implementation doesn't need self.
    # pylint: disable=no-self-use
    def construct(self, _property, value):
        return value

    def __call__(self, property_, value) -> Maybe[T]:
        """Validate and convert input data against the element.

        Runs validators defined on the `validators` property, and calls
        `construct` on the input.
        """
        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            value = self.default
        for validator in self.validators:
            validator(property_, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(property_, value)
