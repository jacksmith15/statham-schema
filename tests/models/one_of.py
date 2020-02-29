from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import converters as con, validators as val
from statham.validators import NotPassed


@attrs(kw_only=True)
class StringWrapper:
    """StringWrapper"""

    _required: ClassVar[List[str]] = ["string_prop"]

    string_prop: str = attrib(
        validator=[val.instance_of(str), val.min_length(3)]
    )


@attrs(kw_only=True)
class StringAndIntegerWrapper:
    """StringAndIntegerWrapper"""

    _required: ClassVar[List[str]] = ["integer_prop"]

    string_prop: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str), val.max_length(5)], default=NotPassed()
    )
    integer_prop: int = attrib(validator=[val.instance_of(int)])


@attrs(kw_only=True)
class OtherStringWrapper:
    """OtherStringWrapper"""

    _required: ClassVar[List[str]] = []

    string_prop: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class Model:
    """Model"""

    _required: ClassVar[List[str]] = []

    primitive: Union[str, int, NotPassed] = attrib(
        validator=[
            val.instance_of(str, int),
            val.min_length(3),
            val.minimum(3),
        ],
        converter=con.one_of_instantiate(),  # type: ignore
        default=NotPassed(),
    )
    objects: Union[StringWrapper, StringAndIntegerWrapper, NotPassed] = attrib(
        validator=[val.instance_of(StringWrapper, StringAndIntegerWrapper)],
        converter=con.one_of_instantiate(
            StringWrapper, StringAndIntegerWrapper
        ),  # type: ignore
        default=NotPassed(),
    )
    mixed: Union[OtherStringWrapper, str, NotPassed] = attrib(
        validator=[val.instance_of(OtherStringWrapper, str)],
        converter=con.one_of_instantiate(OtherStringWrapper),  # type: ignore
        default=NotPassed(),
    )
