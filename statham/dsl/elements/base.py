from abc import ABC
import inspect
from typing import Any, Callable, List

from statham.dsl.constants import NotPassed


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
        """Dynamically construct the repr to match valie instantiation."""
        param_strings = []
        parameters = list(
            inspect.signature(type(self).__init__).parameters.values()
        )[1:]
        for param in parameters:
            value = getattr(self, param.name, None)
            if value == param.default:
                continue
            if param.kind == param.KEYWORD_ONLY:
                param_strings.append(f"{param.name}={repr(value)}")
            else:
                param_strings.append(repr(value))
        param_string = ", ".join(param_strings)
        return f"{type(self).__name__}({param_string})"
