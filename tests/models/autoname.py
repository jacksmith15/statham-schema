from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import converters as con, validators as val
from statham.validators import NotPassed


@attrs(kw_only=True)
class Items:
    """items"""

    _required: ClassVar[List[str]] = []

    string_property: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class Items1:
    """items1"""

    _required: ClassVar[List[str]] = []

    integer_property: Union[int, NotPassed] = attrib(
        validator=[val.instance_of(int)], default=NotPassed()
    )


@attrs(kw_only=True)
class Autoname:
    """Test schema for checking auto-naming logic for anonymous schemas."""

    _required: ClassVar[List[str]] = []

    list_of_strings: Union[List[Union[Items, NotPassed]], NotPassed] = attrib(
        validator=[val.instance_of(list)],
        converter=con.map_instantiate(Items),  # type: ignore
        default=NotPassed(),
    )
    list_of_integers: Union[List[Union[Items1, NotPassed]], NotPassed] = attrib(
        validator=[val.instance_of(list)],
        converter=con.map_instantiate(Items1),  # type: ignore
        default=NotPassed(),
    )
