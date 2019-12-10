from functools import partial
from logging import getLogger
import re
from typing import Callable, Dict, Type, Union
from uuid import UUID
import warnings

# False positive on `ParserError` import.
from dateutil.parser import parse as parse_datetime, ParserError  # type: ignore

from statham.exceptions import ValidationError


LOGGER = getLogger(__name__)


class _FormatString:
    """Extendable format string register."""

    def __init__(self, name: str):
        self._callable_register: Dict[str, Callable[[str], bool]] = {}
        self.__name__: str = name

    def register(self, format_string: str) -> Callable:
        def _register_callable(is_format: Callable[[str], bool]):
            self._callable_register[format_string] = is_format

        return _register_callable

    def __call__(self, format_string: str, value: str) -> bool:
        if format_string not in self._callable_register:
            full_name = f"{self.__module__}.{self.__name__}"
            warnings.warn(
                (
                    f"No validator found for format string {format_string}. "
                    f"To register new formats, please register a checker with "
                    f"{full_name} as follows:\n"
                    f"```\n"
                    f"@{self.__name__}({format_string})\n"
                    f"def is_{format_string.replace('-', '_')}value) -> bool:\n"
                    f"    ...\n"
                    f"```"
                ),
                RuntimeWarning,
            )
            return True
        return self._callable_register[format_string](value)


format_checker: _FormatString = _FormatString("format_checker")


@format_checker.register("uuid")
def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
    except (ValueError, TypeError):
        return False
    return True


@format_checker.register("date-time")
def _is_date_time(value: str) -> bool:
    try:
        parse_datetime(value)
    except (ParserError, TypeError):
        return False
    return True


def on_types(*type_args: Type) -> Callable:
    """Decorator factory to limit scope of validators to given types."""

    def _validate_if_types(validator: Callable) -> Callable:
        """Return a wrapped version of `validator` to negotiate type."""

        def _inner_validator(instance, attribute, value) -> None:
            if not isinstance(value, type_args):
                return
            validator(instance, attribute, value)

        return _inner_validator

    return _validate_if_types


def raises(message: str) -> Callable:
    """Decorator factory which declares error message for validator."""

    def validate_with_error_message(validator: Callable) -> Callable:
        """Return an attrs compatible validator which raises outer error.

        :param validator: Similar to `attrs` validator interface, but
            accepting an additional argument, which is the error to
            raise if validation fails.
        :return: `attrs` compliant validator.
        """

        def inner_validator(instance, attribute, value) -> None:
            validator(
                instance,
                attribute,
                value,
                partial(ValidationError, instance, attribute, value, message),
            )

        return inner_validator

    return validate_with_error_message


def min_items(minimum_items: int) -> Callable:
    @on_types(list)
    @raises(f"Must contain at least {minimum_items} items.")
    def _min_items(_instance, _attribute, value, error):
        if len(value) < minimum_items:
            raise error()

    return _min_items


def max_items(maximum_items: int) -> Callable:
    @on_types(list)
    @raises(f"Must contain fewer than {maximum_items} items.")
    def _max_items(_instance, _attribute, value, error):
        if len(value) > maximum_items:
            raise error()

    return _max_items


def minimum(minimum_value: Union[int, float]) -> Callable:
    @on_types(int, float)
    @raises(f"Must be greater than or equal to {minimum_value}.")
    def _minimum(_instance, _attribute, value, error):
        if value < minimum_value:
            raise error()

    return _minimum


def maximum(maximum_value: Union[int, float]) -> Callable:
    @on_types(int, float)
    @raises(f"Must be less than or equal to {maximum_value}.")
    def _maximum(_instance, _attribute, value, error):
        if value > maximum_value:
            raise error()

    return _maximum


def exclusive_minimum(exclusive_minimum_value: Union[int, float]) -> Callable:
    @on_types(int, float)
    @raises(f"Must be strictly greater than {exclusive_minimum_value}.")
    def _exclusive_minimum(_instance, _attribute, value, error):
        if value <= exclusive_minimum_value:
            raise error()

    return _exclusive_minimum


def exclusive_maximum(exclusive_maximum_value: Union[int, float]) -> Callable:
    @on_types(int, float)
    @raises(f"Must be strictly less than {exclusive_maximum_value}.")
    def _exclusive_maximum(_instance, _attribute, value, error):
        if value >= exclusive_maximum_value:
            raise error()

    return _exclusive_maximum


def multiple_of(multiple_value: Union[int, float]) -> Callable:
    @on_types(int, float)
    @raises(f"Must be a multiple of {multiple_value}.")
    def _multiple_of(_instance, _attribute, value, error):
        if value % multiple_value:
            raise error()

    return _multiple_of


def has_format(format_string: str) -> Callable:
    @on_types(str)
    @raises(f"Must match format described by {repr(format_string)}.")
    def _format(_instance, _attribute, value, error):
        if not format_checker(format_string, value):
            raise error()

    return _format


def pattern(re_pattern: str) -> Callable:
    @on_types(str)
    @raises(f"Must match regex pattern {repr(re_pattern)}.")
    def _pattern(_instance, _attribute, value, error):
        if not re.match(re_pattern, value):
            raise error()

    return _pattern


def min_length(min_length_value: int) -> Callable:
    @on_types(str)
    @raises(f"Must be at least {min_length_value} characters long.")
    def _min_length_value(_instance, _attribute, value, error):
        if len(value) < min_length_value:
            raise error()

    return _min_length_value


def max_length(max_length_value: int) -> Callable:
    @on_types(str)
    @raises(f"Must be at most {max_length_value} characters long.")
    def _max_length_value(_instance, _attribute, value, error):
        if len(value) > max_length_value:
            raise error()

    return _max_length_value


class NotPassed:
    """Singleton similar to NoneType.

    To distinguish between arguments not passed, and arguments passed as
    None.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Enforce singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __repr__(self) -> str:
        return "NotPassed"

    def __bool__(self) -> bool:
        return False


def instance_of(*types: Type) -> Callable:
    type_names = f"({', '.join((type_.__name__ for type_ in types))})"

    @raises(f"Must be of type {type_names}.")
    def _instance_of(instance, attribute, value, error):
        # Validator acts as a method.
        # pylint: disable=protected-access
        if value == NotPassed() and attribute.name not in instance._required:
            return
        if not isinstance(value, types):
            raise error()

    return _instance_of


SCHEMA_ATTRIBUTE_VALIDATORS: Dict[str, Callable] = {
    "minItems": min_items,
    "maxItems": max_items,
    "minimum": minimum,
    "maximum": maximum,
    "exclusiveMinimum": exclusive_minimum,
    "exclusiveMaximum": exclusive_maximum,
    "multipleOf": multiple_of,
    "format": has_format,
    "pattern": pattern,
    "minLength": min_length,
    "maxLength": max_length,
}
"""Mapping of `Schema` attributes to validators."""
