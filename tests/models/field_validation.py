from typing import ClassVar, List, Type

from attr import attrs, attrib

# TODO: Import only what is needed.
# pylint: disable=wildcard-import,unused-wildcard-import
from jsonschema_objects.validators import *


def instantiate(model: Type):
    def _convert(kwargs):
        return model(**kwargs)

    return _convert


def map_instantiate(model: Type):
    def _convert(list_kwargs):
        return [model(**kwargs) for kwargs in list_kwargs]

    return _convert


@attrs(kw_only=True)
class Model:
    """Model"""

    _required: ClassVar[List[str]] = []

    string_no_validation: str = attrib(
        validator=[instance_of(str)], default=NotPassed()
    )
    string_default: str = attrib(validator=[instance_of(str)], default="foo")
    string_format_uuid: str = attrib(
        validator=[instance_of(str), has_format("uuid")], default=NotPassed()
    )
    string_format_date_time: str = attrib(
        validator=[instance_of(str), has_format("date-time")],
        default=NotPassed(),
    )
    string_format_uri: str = attrib(
        validator=[instance_of(str), has_format("uri")], default=NotPassed()
    )
    string_pattern: str = attrib(
        validator=[instance_of(str), pattern(r"^(foo|bar).*")],
        default=NotPassed(),
    )
    string_minLength: str = attrib(
        validator=[instance_of(str), min_length(3)], default=NotPassed()
    )
    string_maxLength: str = attrib(
        validator=[instance_of(str), max_length(3)], default=NotPassed()
    )
    integer_no_validation: int = attrib(
        validator=[instance_of(int)], default=NotPassed()
    )
    integer_default: int = attrib(validator=[instance_of(int)], default=1)
    integer_minimum: int = attrib(
        validator=[instance_of(int), minimum(3)], default=NotPassed()
    )
    integer_exclusiveMinimum: int = attrib(
        validator=[instance_of(int), exclusive_minimum(3)], default=NotPassed()
    )
    integer_maximum: int = attrib(
        validator=[instance_of(int), maximum(3)], default=NotPassed()
    )
    integer_exclusiveMaximum: int = attrib(
        validator=[instance_of(int), exclusive_maximum(3)], default=NotPassed()
    )
    integer_multipleOf: int = attrib(
        validator=[instance_of(int), multiple_of(2)], default=NotPassed()
    )
    number_no_validation: float = attrib(
        validator=[instance_of(float)], default=NotPassed()
    )
    number_default: float = attrib(validator=[instance_of(float)], default=1.5)
    number_minimum: float = attrib(
        validator=[instance_of(float), minimum(2.5)], default=NotPassed()
    )
    number_exclusiveMinimum: float = attrib(
        validator=[instance_of(float), exclusive_minimum(2.5)],
        default=NotPassed(),
    )
    number_maximum: float = attrib(
        validator=[instance_of(float), maximum(2.5)], default=NotPassed()
    )
    number_exclusiveMaximum: float = attrib(
        validator=[instance_of(float), exclusive_maximum(2.5)],
        default=NotPassed(),
    )
    number_multipleOf: float = attrib(
        validator=[instance_of(float), multiple_of(2.5)], default=NotPassed()
    )
    boolean_no_validation: bool = attrib(
        validator=[instance_of(bool)], default=NotPassed()
    )
    boolean_default: bool = attrib(validator=[instance_of(bool)], default=True)
    null_no_validation: None = attrib(
        validator=[instance_of(type(None))], default=NotPassed()
    )
