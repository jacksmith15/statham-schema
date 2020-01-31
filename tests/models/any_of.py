from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import converters as con, validators as val
from statham.validators import NotPassed


@attrs(kw_only=True)
class FooStringMinLength:
    """FooStringMinLength"""

    _required: ClassVar[List[str]] = ["foo"]

    foo: str = attrib(validator=[val.instance_of(str), val.min_length(3)])


@attrs(kw_only=True)
class BarIntegerFooString:
    """BarIntegerFooString"""

    _required: ClassVar[List[str]] = ["bar"]

    foo: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str), val.max_length(5)], default=NotPassed()
    )
    bar: int = attrib(validator=[val.instance_of(int)])


@attrs(kw_only=True)
class FooString:
    """FooString"""

    _required: ClassVar[List[str]] = []

    foo: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class Model:
    """Model"""

    _required: ClassVar[List[str]] = []

    primitive: Union[str, int, NotPassed] = attrib(
        validator=[val.instance_of(str, int)], default=NotPassed()
    )
    objects: Union[FooStringMinLength, BarIntegerFooString, NotPassed] = attrib(
        validator=[val.instance_of(FooStringMinLength, BarIntegerFooString)],
        converter=con.any_of_instantiate(
            FooStringMinLength, BarIntegerFooString
        ),  # type: ignore
        default=NotPassed(),
    )
    mixed: Union[FooString, str, NotPassed] = attrib(
        validator=[val.instance_of(FooString, str)],
        converter=con.any_of_instantiate(FooString),  # type: ignore
        default=NotPassed(),
    )
