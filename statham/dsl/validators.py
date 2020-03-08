from functools import wraps
from logging import getLogger
import re
from typing import Any, Callable, Dict, Type, Union
from uuid import UUID
import warnings

from dateutil.parser import parse as parse_datetime, ParserError  # type: ignore

from statham.dsl.constants import NotPassed
from statham.dsl.exceptions import ValidationError


LOGGER = getLogger(__name__)


class _FormatString:
    """Extendable format string register.

    # TODO: Built-in formats.
    """

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


Validator = Callable[[Any, Any], None]


def on_types(*type_args: Type) -> Callable[[Validator], Validator]:
    """Decorator factory to limit scope of validators to given types."""

    def _validate_if_types(validator: Validator) -> Validator:
        """Return a wrapped version of `validator` to negotiate type."""

        def _inner_validator(value, property_) -> None:
            if not isinstance(value, type_args):
                return
            validator(value, property_)

        return _inner_validator

    return _validate_if_types


def raises(message: str) -> Callable[[Validator], Validator]:
    """Decorator factory which declares error message for validator.

    The aim of this is to ensure validators deal with a single error
    state.
    """

    def validate_with_error_message(validator: Validator) -> Validator:
        """Return a DSL compatible validator which raises outer error.

        :param validator: DSL validator interface, but may simply raise
            `ValidationError` without a message.
        :return: DSL compliant validator.
        """

        @wraps(validator)
        def inner_validator(value, property_) -> None:
            try:
                validator(value, property_)
            except ValidationError:
                raise ValidationError.from_validator(property_, value, message)

        return inner_validator

    return validate_with_error_message


def min_items(minimum_items: int) -> Validator:
    @on_types(list)
    @raises(f"Must contain at least {minimum_items} items.")
    def _min_items(value, _property):
        if len(value) < minimum_items:
            raise ValidationError

    return _min_items


def max_items(maximum_items: int) -> Validator:
    @on_types(list)
    @raises(f"Must contain fewer than {maximum_items} items.")
    def _max_items(value, _property):
        if len(value) > maximum_items:
            raise ValidationError

    return _max_items


def minimum(minimum_value: Union[int, float]) -> Validator:
    @on_types(int, float)
    @raises(f"Must be greater than or equal to {minimum_value}.")
    def _minimum(value, _property):
        if value < minimum_value:
            raise ValidationError

    return _minimum


def maximum(maximum_value: Union[int, float]) -> Validator:
    @on_types(int, float)
    @raises(f"Must be less than or equal to {maximum_value}.")
    def _maximum(value, _property):
        if value > maximum_value:
            raise ValidationError

    return _maximum


def exclusive_minimum(exclusive_minimum_value: Union[int, float]) -> Validator:
    @on_types(int, float)
    @raises(f"Must be strictly greater than {exclusive_minimum_value}.")
    def _exclusive_minimum(value, _property):
        if value <= exclusive_minimum_value:
            raise ValidationError

    return _exclusive_minimum


def exclusive_maximum(exclusive_maximum_value: Union[int, float]) -> Validator:
    @on_types(int, float)
    @raises(f"Must be strictly less than {exclusive_maximum_value}.")
    def _exclusive_maximum(value, _property):
        if value >= exclusive_maximum_value:
            raise ValidationError

    return _exclusive_maximum


def multiple_of(multiple_value: Union[int, float]) -> Validator:
    @on_types(int, float)
    @raises(f"Must be a multiple of {multiple_value}.")
    def _multiple_of(value, _property):
        if value % multiple_value:
            raise ValidationError

    return _multiple_of


def has_format(format_string: str) -> Validator:
    @on_types(str)
    @raises(f"Must match format described by {repr(format_string)}.")
    def _format(value, _property):
        if not format_checker(format_string, value):
            raise ValidationError

    return _format


def pattern(re_pattern: str) -> Validator:
    @on_types(str)
    @raises(f"Must match regex pattern {repr(re_pattern)}.")
    def _pattern(value, _property):
        if not re.match(re_pattern, value):
            raise ValidationError

    return _pattern


def min_length(min_length_value: int) -> Validator:
    @on_types(str)
    @raises(f"Must be at least {min_length_value} characters long.")
    def _min_length_value(value, _property):
        if len(value) < min_length_value:
            raise ValidationError

    return _min_length_value


def max_length(max_length_value: int) -> Validator:
    @on_types(str)
    @raises(f"Must be at most {max_length_value} characters long.")
    def _max_length_value(value, _property):
        if len(value) > max_length_value:
            raise ValidationError

    return _max_length_value


def instance_of(*types: Type) -> Validator:
    type_names = f"({', '.join((type_.__name__ for type_ in types))})"

    @raises(f"Must be of type {type_names}.")
    def _instance_of(value, _property):
        if value == NotPassed():
            return
        if not isinstance(value, types):
            raise ValidationError

    return _instance_of


def required(is_required: bool) -> Validator:
    @raises(f"Not passed but is required.")
    def _required(value, _property):
        if value == NotPassed() and is_required:
            raise ValidationError

    return _required


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
"""Mapping of JSON Schema keywords to validators."""
