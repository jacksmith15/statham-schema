import re
from typing import Callable, Dict, Type, Union
from uuid import UUID

# False positive on `ParserError` import.
from dateutil.parser import parse as parse_datetime, ParserError  # type: ignore


class _FormatString:
    """Extendable format string register."""

    def __init__(self):
        self._callable_register: Dict[str, Callable[[str], bool]] = {}

    def register(self, format_string: str) -> Callable:
        def _register_callable(is_format: Callable[[str], bool]):
            self._callable_register[format_string] = is_format

        return _register_callable

    def __call__(self, format_string: str, value: str) -> bool:
        if format_string not in self._callable_register:
            raise KeyError(
                f"No validator found for format string {format_string}"
            )
        return self._callable_register[format_string](value)


format_checker: _FormatString = _FormatString()


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


def valid_types(*type_args: Type) -> Callable:
    def validate_if_types(validator: Callable) -> Callable:
        def inner_validator(instance, attribute, value) -> None:
            if not isinstance(value, type_args):
                return
            validator(instance, attribute, value)

        return inner_validator

    return validate_if_types


def min_items(minimum_items: int) -> Callable:
    @valid_types(list)
    def _min_items(_instance, _attribute, value):
        if len(value) < minimum_items:
            raise ValueError

    return _min_items


def max_items(maximum_items: int) -> Callable:
    @valid_types(list)
    def _max_items(_instance, _attribute, value):
        if len(value) > maximum_items:
            raise ValueError

    return _max_items


def minimum(minimum_value: Union[int, float]) -> Callable:
    @valid_types(int, float)
    def _minimum(_instance, _attribute, value):
        if value < minimum_value:
            raise ValueError

    return _minimum


def maximum(maximum_value: Union[int, float]) -> Callable:
    @valid_types(int, float)
    def _maximum(_instance, _attribute, value):
        if value > maximum_value:
            raise ValueError

    return _maximum


def exclusive_minimum(exclusive_minimum_value: Union[int, float]) -> Callable:
    @valid_types(int, float)
    def _exclusive_minimum(_instance, _attribute, value):
        if value <= exclusive_minimum_value:
            raise ValueError

    return _exclusive_minimum


def exclusive_maximum(exclusive_maximum_value: Union[int, float]) -> Callable:
    @valid_types(int, float)
    def _exclusive_maximum(_instance, _attribute, value):
        if value >= exclusive_maximum_value:
            raise ValueError

    return _exclusive_maximum


def multiple_of(multiple_value: Union[int, float]) -> Callable:
    @valid_types(int, float)
    def _multiple_of(_instance, _attribute, value):
        if value % multiple_value:
            raise ValueError

    return _multiple_of


def has_format(format_string: str) -> Callable:
    @valid_types(str)
    def _format(_instance, _attribute, value):
        if not format_checker(format_string, value):
            raise ValueError

    return _format


def pattern(re_pattern: str) -> Callable:
    @valid_types(str)
    def _pattern(_instance, _attribute, value):
        if not re.match(re_pattern, value):
            raise ValueError

    return _pattern


def min_length(min_length_value: int) -> Callable:
    @valid_types(str)
    def _min_length_value(_instance, _attribute, value):
        if len(value) < min_length_value:
            raise ValueError

    return _min_length_value


def max_length(max_length_value: int) -> Callable:
    @valid_types(str)
    def _max_length_value(_instance, _attribute, value):
        if len(value) > max_length_value:
            raise ValueError

    return _max_length_value


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
