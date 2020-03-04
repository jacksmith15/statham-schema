from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import validators as val

# pylint: disable=unused-import
from statham.converters import AnyOf, Array, instantiate, OneOf

# pylint: enable=unused-import
from statham.dsl.constants import NotPassed


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

    _required: ClassVar[List[str]] = ["string_prop"]

    string_prop: str = attrib(
        validator=[val.instance_of(str), val.max_length(5)]
    )
    integer_prop: Union[int, NotPassed] = attrib(
        validator=[val.instance_of(int)], default=NotPassed()
    )


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
        converter=instantiate(AnyOf()),  # type: ignore
        default=NotPassed(),
    )
    objects: Union[StringWrapper, StringAndIntegerWrapper, NotPassed] = attrib(
        validator=[val.instance_of(StringWrapper, StringAndIntegerWrapper)],
        converter=instantiate(  # type: ignore
            AnyOf(StringWrapper, StringAndIntegerWrapper)
        ),
        default=NotPassed(),
    )
    mixed: Union[OtherStringWrapper, str, NotPassed] = attrib(
        validator=[val.instance_of(OtherStringWrapper, str)],
        converter=instantiate(AnyOf(OtherStringWrapper)),  # type: ignore
        default=NotPassed(),
    )
