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
        if attribute.name not in instance._required and value == NOT_PASSED:
            return
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
class NestedSchema:
    """nested_schema"""

    _required: ClassVar[List[str]] = ["id"]

    id = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(str),
                    matches_re(
                        r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]"
                        r"{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
                        func=re.match,
                    ),
                ],
            )
        )
    )
    timestamp = attrib(
        validator=list(
            map(
                if_passed,
                [
                    instance_of(str),
                    matches_re(
                        (
                            r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
                            r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):"
                            r"([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]"
                            r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
                        ),
                        func=re.match,
                    ),
                ],
            )
        ),
        default=NOT_PASSED,
    )
    version = attrib(
        validator=list(map(if_passed, [instance_of(int)])), default=0
    )
    annotation = attrib(
        validator=list(map(if_passed, [instance_of(str)])),
        default="unannotated",
    )


@attrs(kw_only=True)
class SimpleSchema:
    """This is a simple object."""

    _required: ClassVar[List[str]] = ["related"]

    related = attrib(
        validator=list(map(if_passed, [instance_of(NestedSchema)])),
        converter=instantiate(NestedSchema),  # type: ignore
    )
    amount = attrib(
        validator=list(map(if_passed, [instance_of(float)])), default=NOT_PASSED
    )
    children = attrib(
        validator=list(map(if_passed, [instance_of(list)])),
        converter=map_instantiate(NestedSchema),  # type: ignore
        default=NOT_PASSED,
    )
