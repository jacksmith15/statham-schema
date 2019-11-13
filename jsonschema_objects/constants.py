from enum import auto, Flag, unique
from functools import reduce
from typing import Callable, Type, Union


INDENT = " " * 4


NotProvidedType = type(
    "NotProvidedType", tuple(), {"__repr__": lambda self: "<NOTPROVIDED>"}
)
NOT_PROVIDED: NotProvidedType = NotProvidedType()


not_required: Callable[[Type], Type] = lambda Type_: Union[Type_, NotProvidedType]
"""Similar to `typing.Optional` but for the NotProvidedType."""


IGNORED_SCHEMA_KEYWORDS = ("$schema", "definitions")
"""Keywords to ignore from jsonschemas when parsing."""


@unique
class TypeEnum(Flag):
    OBJECT = auto()
    ARRAY = auto()
    NUMBER = auto()
    INTEGER = auto()
    STRING = auto()
    NULL = auto()


_JSON_SCHEMA_TYPE_MAP = (
    ("object", TypeEnum.OBJECT),
    ("array", TypeEnum.ARRAY),
    ("number", TypeEnum.NUMBER),
    ("integer", TypeEnum.INTEGER),
    ("string", TypeEnum.STRING),
    ("null", TypeEnum.NULL),
)

_TYPE_LOOKUP = dict(_JSON_SCHEMA_TYPE_MAP)


def get_flag(*types: str) -> TypeEnum:
    """Get type flag for jsonschema type representation."""
    if not types:
        raise ValueError("Need at least one type.")
    unknown = set(types) - set(_TYPE_LOOKUP)
    if unknown:
        raise ValueError(f"Unknown JSONSchema types: {unknown}")
    if len(types) == 1:
        return _TYPE_LOOKUP[next(iter(types))]
    return reduce(lambda x, y: x | y, map(_TYPE_LOOKUP.get, types))


_ENUM_LOOKUP = {enum: keyword for keyword, enum in _JSON_SCHEMA_TYPE_MAP}


def get_type(flag: TypeEnum) -> Union[str]:
    """Get jsonschema type representation of type flag."""
    if flag in _ENUM_LOOKUP:
        return _ENUM_LOOKUP[flag]
    return [_ENUM_LOOKUP[_flag] for _flag in _ENUM_LOOKUP if _flag & flag]
