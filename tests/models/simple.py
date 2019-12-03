from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import converters as con, validators as val
from statham.validators import NotPassed


@attrs(kw_only=True)
class NestedSchema:
    """nested_schema"""

    _required: ClassVar[List[str]] = ["id"]

    id: str = attrib(
        validator=[
            val.instance_of(str),
            val.has_format("uuid"),
            val.pattern(
                "^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F"
                "]{4}\\-[0-9a-fA-F]{12}$"
            ),
        ]
    )
    timestamp: Union[str, NotPassed] = attrib(
        validator=[
            val.instance_of(str),
            val.has_format("date-time"),
            val.pattern(
                "^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[1"
                "2][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\\.[0-9]"
                "+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
            ),
        ],
        default=NotPassed(),
    )
    version: Union[int, NotPassed] = attrib(
        validator=[val.instance_of(int)], default=0
    )
    annotation: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default="unannotated"
    )


@attrs(kw_only=True)
class SimpleSchema:
    """This is a simple object."""

    _required: ClassVar[List[str]] = ["related"]

    related: NestedSchema = attrib(
        validator=[val.instance_of(NestedSchema)],
        converter=con.instantiate(NestedSchema),  # type: ignore
    )
    amount: Union[float, NotPassed] = attrib(
        validator=[val.instance_of(float)], default=NotPassed()
    )
    children: Union[List[Union[NestedSchema, NotPassed]], NotPassed] = attrib(
        validator=[val.instance_of(list)],
        converter=con.map_instantiate(NestedSchema),  # type: ignore
        default=NotPassed(),
    )
