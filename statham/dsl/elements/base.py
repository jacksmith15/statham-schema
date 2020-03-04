from abc import ABC
from typing import Any, Callable, List

from statham.dsl.constants import NotPassed
from statham.dsl.helpers import custom_repr


class Element(ABC):
    """Schema element for composing instantiation logic."""

    default: Any

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

    def __call__(self, property_, value):
        """Allow different instantiation logic per sentinel."""
        if not isinstance(self.default, NotPassed) and isinstance(
            value, NotPassed()
        ):
            value = self.default
        for validator in self.validators:
            validator(property_, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(property_, value)

    def __repr__(self):
        """Dynamically construct the repr to match value instantiation."""
        return custom_repr(self)
