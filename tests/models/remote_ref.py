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
class NestedRemote:
    """Local reference nested in remote reference"""

    _required: ClassVar[List[str]] = []

    name: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )


@attrs(kw_only=True)
class Remote:
    """Remote ref in sub-directory."""

    _required: ClassVar[List[str]] = []

    name: Union[str, NotPassed] = attrib(
        validator=[val.instance_of(str)], default=NotPassed()
    )
    nested: Union[NestedRemote, NotPassed] = attrib(
        validator=[val.instance_of(NestedRemote)],
        converter=con.instantiate(NestedRemote),  # type: ignore
        default=NotPassed(),
    )


@attrs(kw_only=True)
class Model:
    """Model defined with remote refs."""

    _required: ClassVar[List[str]] = []

    filesystem_remote_ref_flat: Union[Category, NotPassed] = attrib(
        validator=[val.instance_of(Category)],
        converter=con.instantiate(Category),  # type: ignore
        default=NotPassed(),
    )
    filesystem_remote_ref_directory: Union[Remote, NotPassed] = attrib(
        validator=[val.instance_of(Remote)],
        converter=con.instantiate(Remote),  # type: ignore
        default=NotPassed(),
    )
