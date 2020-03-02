from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import validators as val

# pylint: disable=unused-import
from statham.converters import AnyOf, Array, instantiate, OneOf

# pylint: enable=unused-import
from statham.validators import NotPassed


@attrs(kw_only=True)
class ListOfStringsItem:
    """list_of_stringsItem"""

    _required: ClassVar[List[str]] = []

    string_property: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class ListOfIntegersItem:
    """list_of_integersItem"""

    _required: ClassVar[List[str]] = []

    integer_property: Union[int, NotPassed] = attrib(
        validator=[val.instance_of(int)], default=NotPassed()
    )


@attrs(kw_only=True)
class ListAnyOfItem0:
    """list_any_ofItem0"""

    _required: ClassVar[List[str]] = []

    string_prop: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class ListAnyOfItem1:
    """list_any_ofItem1"""

    _required: ClassVar[List[str]] = []

    integer_prop: Union[int, NotPassed] = attrib(
        validator=[val.instance_of(int)], default=NotPassed()
    )


@attrs(kw_only=True)
class Autoname:
    """Test schema for checking auto-naming logic for anonymous schemas."""

    _required: ClassVar[List[str]] = []

    list_of_strings: Union[
        List[Union[ListOfStringsItem, NotPassed]], NotPassed
    ] = attrib(
        validator=[val.instance_of(list)],
        converter=instantiate(Array(ListOfStringsItem)),  # type: ignore
        default=NotPassed(),
    )
    list_of_integers: Union[
        List[Union[ListOfIntegersItem, NotPassed]], NotPassed
    ] = attrib(
        validator=[val.instance_of(list)],
        converter=instantiate(Array(ListOfIntegersItem)),  # type: ignore
        default=NotPassed(),
    )
    list_any_of: Union[
        List[Union[ListAnyOfItem0, ListAnyOfItem1, str, NotPassed]], NotPassed
    ] = attrib(
        validator=[val.instance_of(list)],
        converter=instantiate(  # type: ignore
            Array(AnyOf(ListAnyOfItem0, ListAnyOfItem1))
        ),
        default=NotPassed(),
    )
