from functools import partial
import re
from typing import Callable, ClassVar, List, Type

from attr import attrs, attrib


NOT_PASSED = type(
    "NotPassed",
    tuple(),
    {"__repr__": lambda self: "<NOTPASSED>", "__bool__": lambda self: False},
)()


def instance_of(*types: Type) -> Callable:
    def validate_type(instance, attribute, value):
        if attribute.name not in instance.required and value == NOT_PASSED:
            return
        if not isinstance(value, types):
            raise TypeError(
                f"{attribute.name} must by type {types}, got {value}."
            )

    return validate_type


def matches_pattern(pattern: str) -> Callable:
    def validate_pattern(instance, attribute, value):
        if value == NOT_PASSED:
            return
        if not re.match(pattern, value):
            raise ValueError(
                f"{attribute.name} must match pattern {pattern}. Got {value}."
            )

    return validate_pattern


@attrs(kw_only=True)
class NestedSchema:
    """nested_schema"""

    required: ClassVar[List[str]] = ["id"]

    id = attrib(
        validator=[
            instance_of(str),
            matches_pattern(
                r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$"
            ),
        ]
    )
    timestamp = attrib(
        validator=[
            instance_of(str),
            matches_pattern(
                r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
            ),
        ],
        default=NOT_PASSED,
    )
    version = attrib(validator=[instance_of(int)], default=0)
    annotation = attrib(validator=[instance_of(str)], default="unannotated")


@attrs(kw_only=True)
class SimpleSchema:
    """This is a simple object."""

    required: ClassVar[List[str]] = ["related"]

    related = attrib(
        validator=[instance_of(NestedSchema)],
        converter=lambda _: NestedSchema(**_),
    )
    amount = attrib(validator=[instance_of(float)], default=NOT_PASSED)
    children = attrib(
        validator=[instance_of(list)],
        converter=partial(map, lambda _: NestedSchema(**_)),
        default=NOT_PASSED,
    )
