from functools import wraps
import inspect
from typing import (
    Any,
    Callable,
    Container,
    Dict,
    Iterable,
    List,
    Tuple,
    Type,
    TypeVar,
    Union,
)


class Args:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def apply(self, function):
        return function(*self.args, **self.kwargs)

    def __repr__(self):
        arg_string = ", ".join([repr(arg) for arg in self.args])
        kwarg_string = ", ".join(
            [f"{key}={repr(value)}" for key, value in self.kwargs.items()]
        )
        return "(" + ", ".join(filter(None, [arg_string, kwarg_string])) + ")"


def custom_repr_args(self, **overrides: Any) -> Args:
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    parameters = list(
        inspect.signature(type(self).__init__).parameters.values()
    )[1:]
    for param in parameters:
        value = overrides.get(param.name, getattr(self, param.name, None))
        if value == param.default:
            continue
        if param.kind == param.VAR_POSITIONAL:
            args.extend(value or [])
        elif param.kind == param.KEYWORD_ONLY:
            kwargs[param.name] = value
        else:
            args.append(value)
    return Args(*args, **kwargs)


def custom_repr(self, **overrides: Any) -> str:
    """Dynamically construct the repr to match value instantiation.

    Shows the class name and attribute values, where they differ from
    defaults.

    :param overrides: Overwrites of instance attribute values for the
        repr.
    :return: String representation of :paramref:`custom_repr.self`.
    """
    return f"{type(self).__name__}{repr(custom_repr_args(self, **overrides))}"


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


T = TypeVar("T")


def split_dict(
    keys: Container[T],
) -> Callable[[Dict[T, Any]], Tuple[Dict[T, Any], Dict[T, Any]]]:
    """Split a dictionary on matching and non-matching keys."""

    def _split(dictionary: Dict[T, Any]) -> Tuple[Dict[T, Any], Dict[T, Any]]:
        match = {key: value for key, value in dictionary.items() if key in keys}
        complement = {
            key: value for key, value in dictionary.items() if key not in keys
        }
        return match, complement

    return _split


def expand(function):
    """Useful for functional operations like map."""
    return lambda args: function(*args)


SequenceItem = TypeVar("SequenceItem")


def remove_duplicates(seq: Iterable[SequenceItem]) -> List[SequenceItem]:
    """Remove duplicates whilst preserving order."""
    seen: List[SequenceItem] = []
    seen_add = seen.append
    return [x for x in seq if not (x in seen or seen_add(x))]
