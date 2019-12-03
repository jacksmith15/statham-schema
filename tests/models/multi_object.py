from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import converters as con, validators as val
from statham.validators import NotPassed


@attrs(kw_only=True)
class Category:
    """Category with required name."""

    _required: ClassVar[List[str]] = ["required_name"]

    required_name: str = attrib(validator=[val.instance_of(str)])


@attrs(kw_only=True)
class Child:
    """Model with name and reference to category."""

    _required: ClassVar[List[str]] = []

    name: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )
    category: Union[Category, NotPassed] = attrib(
        validator=[val.instance_of(Category)],
        converter=con.instantiate(Category),  # type: ignore
        default=NotPassed(),
    )


@attrs(kw_only=True)
class Model:
    """Model with references to children and category."""

    _required: ClassVar[List[str]] = []

    children: Union[List[Union[Child, NotPassed]], NotPassed] = attrib(
        validator=[val.instance_of(list)],
        converter=con.map_instantiate(Child),  # type: ignore
        default=NotPassed(),
    )
    category: Union[Category, NotPassed] = attrib(
        validator=[val.instance_of(Category)],
        converter=con.instantiate(Category),  # type: ignore
        default=NotPassed(),
    )
