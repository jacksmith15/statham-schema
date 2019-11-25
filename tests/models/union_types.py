from typing import ClassVar, List, Type, Union

from attr import attrs, attrib
from statham import validators as val
from statham.validators import NotPassed


def instantiate(model: Type):
    def _convert(kwargs):
        return model(**kwargs)

    return _convert


def map_instantiate(model: Type):
    def _convert(list_kwargs):
        return [model(**kwargs) for kwargs in list_kwargs]

    return _convert


@attrs(kw_only=True)
class Model:
    """Model"""

    _required: ClassVar[List[str]] = []

    number_integer: Union[int, float, NotPassed] = attrib(
        validator=[
            val.instance_of(int, float),
            val.minimum(2.5),
            val.exclusive_maximum(5),
        ],
        default=3.5,
    )
    string_integer: Union[int, str, NotPassed] = attrib(
        validator=[
            val.instance_of(int, str),
            val.minimum(1970),
            val.exclusive_maximum(2050),
            val.has_format("date-time"),
        ],
        default=2000,
    )
    string_null: Union[str, None, NotPassed] = attrib(
        validator=[
            val.instance_of(str, type(None)),
            val.has_format("uuid"),
            val.pattern(
                r"^[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-"
                r"[0-9a-fA-F]{4}\\-[0-9a-fA-F]{12}$"
            ),
        ],
        default=None,
    )
