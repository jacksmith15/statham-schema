import re
from typing import ClassVar, List, Type

from attr import attrs, attrib
from attr.validators import matches_re


NOT_PASSED = type(
    "NotPassed",
    tuple(),
    {"__repr__": lambda self: "<NOTPASSED>", "__bool__": lambda self: False},
)()


def instance_of(*types: Type):
    def validate_type(instance, attribute, value):
        if not isinstance(value, types):
            raise TypeError(
                f"{attribute.name} must by type {types}, got {value}."
            )

    return validate_type


def if_passed(validator):
    def optional_validator(instance, attribute, value):
        if attribute.name not in instance._required and value == NOT_PASSED:
            return
        validator(instance, attribute, value)

    return optional_validator


def fail_unless(function, message=None):
    def check(instance, attribute, value):
        if not function(instance, attribute, value):
            raise ValueError(message)

    return check


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

    string_no_validation = attrib(
        validator=list(map(if_passed, [instance_of(str)])), default=NOT_PASSED
    )
    string_default = attrib(
        validator=list(map(if_passed, [instance_of(str)])), default="foo"
    )
    string_format_uuid = attrib(
        validator=list(map(if_passed, [instance_of(str)])), default=NOT_PASSED
    )
    string_format_date_time = attrib(
        validator=list(map(if_passed, [instance_of(str)])), default=NOT_PASSED
    )
    string_format_uri = attrib(
        validator=list(map(if_passed, [instance_of(str)])), default=NOT_PASSED
    )
    string_pattern = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(str), matches_re(r"^(foo|bar).*", func=re.match)],
            )
        ),
        default=NOT_PASSED,
    )
    string_minLength = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(str),
                    fail_unless(lambda _, __, val: len(val) >= 3),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    string_maxLength = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(str),
                    fail_unless(lambda _, __, val: len(val) <= 3),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    integer_no_validation = attrib(
        validator=list(map(if_passed, [instance_of(int)])), default=NOT_PASSED
    )
    integer_default = attrib(
        validator=list(map(if_passed, [instance_of(int)])), default=1
    )
    integer_minimum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(int), fail_unless(lambda _, __, val: val >= 3)],
            )
        ),
        default=NOT_PASSED,
    )
    integer_exclusiveMinimum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(int), fail_unless(lambda _, __, val: val > 3)],
            )
        ),
        default=NOT_PASSED,
    )
    integer_maximum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(int), fail_unless(lambda _, __, val: val <= 3)],
            )
        ),
        default=NOT_PASSED,
    )
    integer_exclusiveMaximum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(int), fail_unless(lambda _, __, val: val < 3)],
            )
        ),
        default=NOT_PASSED,
    )
    integer_multipleOf = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(int),
                    fail_unless(lambda _, __, val: (val % 2) == 0),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    number_no_validation = attrib(
        validator=list(map(if_passed, [instance_of(float)])), default=NOT_PASSED
    )
    number_default = attrib(
        validator=list(map(if_passed, [instance_of(float)])), default=1.5
    )
    number_minimum = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(float),
                    fail_unless(lambda _, __, val: val >= 2.5),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    number_exclusiveMinimum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(float), fail_unless(lambda _, __, val: val > 2.5)],
            )
        ),
        default=NOT_PASSED,
    )
    number_maximum = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(float),
                    fail_unless(lambda _, __, val: val <= 2.5),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    number_exclusiveMaximum = attrib(
        validator=list(
            map(
                if_passed,
                [instance_of(float), fail_unless(lambda _, __, val: val < 2.5)],
            )
        ),
        default=NOT_PASSED,
    )
    number_multipleOf = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(float),
                    fail_unless(lambda _, __, val: (val % 2.5) == 0),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    boolean_no_validation = attrib(
        validator=list(map(if_passed, [instance_of(bool)])), default=NOT_PASSED
    )
    boolean_default = attrib(
        validator=list(map(if_passed, [instance_of(bool)])), default=True
    )
