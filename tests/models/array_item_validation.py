from typing import ClassVar, List, Union

from attr import attrs, attrib
from statham import validators as val

# pylint: disable=unused-import
from statham.converters import AnyOf, Array, instantiate, OneOf

# pylint: enable=unused-import
from statham.validators import NotPassed


@attrs(kw_only=True)
class Model:
    """Model"""

    _required: ClassVar[List[str]] = []

    list_of_strings: Union[List[Union[str, NotPassed]], NotPassed] = attrib(
        validator=[val.instance_of(list)], default=NotPassed()
    )
