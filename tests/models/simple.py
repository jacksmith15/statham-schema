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
    timestamp: Union[str, NotPassed] = attrib(
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
        default=NotPassed(),
    )
    version: Union[int, NotPassed] = attrib(
        validator=[instance_of(int)], default=0
    )
    annotation: Union[str, NotPassed] = attrib(
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
    amount: Union[float, NotPassed] = attrib(
        validator=[instance_of(float)], default=NotPassed()
    )
    children: Union[List[Union[NestedSchema, NotPassed]], NotPassed] = attrib(
        validator=[instance_of(list)],
        converter=map_instantiate(NestedSchema),  # type: ignore
        default=NotPassed(),
    )
