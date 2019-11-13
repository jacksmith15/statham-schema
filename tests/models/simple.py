from functools import partial

from attr import attrs, attrib
from attr.validators import instance_of


@attrs(kw_only=True)
class NestedSchema:
    """nested_schema"""

    id = attrib(
        validator=[instance_of(str)],
        default=None,
    )
    timestamp = attrib(
        validator=[instance_of(str)],
        default=None,
    )
    version = attrib(
        validator=[instance_of(int)],
        default=0,
    )
    annotation = attrib(
        validator=[instance_of(str)],
        default="unannotated",
    )


@attrs(kw_only=True)
class SimpleSchema:
    """This is a simple object."""

    related = attrib(
        validator=[instance_of(NestedSchema)],
        converter=lambda x: NestedSchema(**x),
    )
    amount = attrib(
        validator=[instance_of(float)],
        default=None,
    )
    children = attrib(
        validator=[instance_of(list)],
        converter=partial(map, NestedSchema),
        default=None,
    )
