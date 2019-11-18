from typing import ClassVar, List, Type

from attr import attrs, attrib

# TODO: Import only what is needed.
# pylint: disable=wildcard-import,unused-wildcard-import
from jsonschema_objects.validators import *


NOT_PASSED = type(
    "NotPassed",
    tuple(),
    {"__repr__": lambda self: "<NOTPASSED>", "__bool__": lambda self: False},
)()


def instance_of(*types: Type):
    def validate_type(instance, attribute, value):
        # This callable acts as a method.
        # pylint: disable=protected-access
        if attribute.name not in instance._required and value == NOT_PASSED:
            return
        if not isinstance(value, types):
            raise TypeError(
                f"{attribute.name} must be type {types}, got {value}."
            )

    return validate_type


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

    id: str = attrib(
        validator=[
            instance_of(str),
            has_format("uuid"),
            pattern(
                r"^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-"
                r"[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$"
            ),
        ]
    )
    timestamp: str = attrib(
        validator=[
            instance_of(str),
            has_format("date-time"),
            pattern(
                r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
                r"(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):"
                r"([0-5][0-9]):([0-5][0-9])(\\.[0-9]+)?(Z|[+-]"
                r"(?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
            ),
        ],
        default=NOT_PASSED,
    )
    version: int = attrib(validator=[instance_of(int)], default=0)
    annotation: str = attrib(
        validator=[instance_of(str)], default="unannotated"
    )


@attrs(kw_only=True)
class SimpleSchema:
    """This is a simple object."""

    _required: ClassVar[List[str]] = ["related"]

    related: NestedSchema = attrib(
        validator=[instance_of(NestedSchema)],
        converter=instantiate(NestedSchema),  # type: ignore
    )
    amount: float = attrib(validator=[instance_of(float)], default=NOT_PASSED)
    children: List[NestedSchema] = attrib(
        validator=[instance_of(list)],
        converter=map_instantiate(NestedSchema),  # type: ignore
        default=NOT_PASSED,
    )
