from functools import wraps
import inspect
from typing import Tuple, Type, Union


def custom_repr(self):
    """Dynamically construct the repr to match value instantiation.

    Shows the class name and attribute values, where they differ from
    defaults.
    """
    param_strings = []
    parameters = list(
        inspect.signature(type(self).__init__).parameters.values()
    )[1:]
    for param in parameters:
        value = getattr(self, param.name, None)
        if value == param.default:
            continue
        if param.kind == param.VAR_POSITIONAL:
            param_strings.extend([repr(sub_val) for sub_val in value or []])
        elif param.kind == param.KEYWORD_ONLY:
            param_strings.append(f"{param.name}={repr(value)}")
        else:
            param_strings.append(repr(value))
    param_string = ", ".join(param_strings)
    return f"{type(self).__name__}({param_string})"


ExceptionTypes = Union[Type[Exception], Tuple[Type[Exception], ...]]


def reraise(catch: ExceptionTypes, throw: Type[Exception], message: str):
    """Decorator factory for re-raising exceptions of a raised in a function."""

    def _decorator(function):
        @wraps(function)
        def _wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except catch as exc:
                raise throw(message) from exc

        return _wrapper

    return _decorator
