from typing import Any, Callable, List, Generic, TypeVar, Union

from statham.dsl.constants import NotPassed
from statham.dsl.helpers import custom_repr


T = TypeVar("T")


class Element(Generic[T]):
    """Schema element for composing instantiation logic."""

    default: Any

    def __repr__(self):
        """Dynamically construct the repr to match value instantiation."""
        return custom_repr(self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return vars(self) == vars(other)

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

    def __call__(self, property_, value) -> Union[T, NotPassed]:
        """Allow different instantiation logic per sentinel."""
        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed
        ):
            value = self.default
        for validator in self.validators:
            validator(property_, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(property_, value)
