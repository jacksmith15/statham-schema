from abc import ABC
import inspect
from typing import Any, List

from statham import validators as val
from statham.validators import NotPassed


class Element(ABC):
    """Schema element for composing instantiation logic."""

    required: bool
    default: Any

    @property
    def type_validator(self):
        return val.null

    @property
    def validators(self) -> List[val.Validator]:
        return [val.required(self.required), self.type_validator]

    # Default implementation doesn't need self.
    # pylint: disable=no-self-use
    def construct(self, _instance, _attribute, value):
        return value

    def __call__(self, instance, attribute, value):
        """Allow different instantiation logic per sentinel."""
        if self.default and value is not NotPassed():
            value = self.default
        for validator in self.validators:
            validator(instance, attribute, value)
        if isinstance(value, NotPassed):
            return value
        return self.construct(instance, attribute, value)

    def __repr__(self):
        """Dynamically construct the repr to match valie instantiation."""
        param_strings = []
        parameters = list(
            inspect.signature(type(self).__init__).parameters.values()
        )[1:]
        for param in parameters:
            value = getattr(self, param.name)
            if value == param.default:
                continue
            if param.kind == param.KEYWORD_ONLY:
                param_strings.append(f"{param.name}={repr(value)}")
            else:
                param_strings.append(repr(value))
        param_string = ", ".join(param_strings)
        return f"{type(self).__name__}({param_string})"
