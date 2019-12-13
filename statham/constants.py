from enum import auto, Flag, unique
from functools import reduce
from typing import Any, Dict, Iterator, List, Tuple, Union


INDENT = " " * 4


JSONElement = Union[Dict[str, Any], List[Any], int, float, bool, None, str]


class NotProvidedType:
    """Singleton for indicating whether a field has been specified.

    Useful to differentiate between e.g. default=None and no default.
    """

    def __repr__(self):
        return "<NOTPROVIDED>"


NOT_PROVIDED: NotProvidedType = NotProvidedType()


IGNORED_SCHEMA_KEYWORDS = (
    # Metadata
    "$id",
    "$schema",
    "definitions",
    "$comment",
    "contentMediaType",
    "contentEncoding",
    "examples",
    "readOnly",
    "writeOnly",
    "deprecated",
    # Not implemented
    "additionalItems",
    "contains",
    "additionalProperties",
    "propertyNames",
    "patternProperties",
    "minProperties",
    "maxProperties",
    "enum",
    "const",
    "uniqueItems",
    # OpenAPI/Swagger
    "example",
    "nullable",
)
"""Keywords to ignore from jsonschemas when parsing."""


@unique
class TypeEnum(Flag):
    OBJECT = auto()
    ARRAY = auto()
    NUMBER = auto()
    INTEGER = auto()
    STRING = auto()
    NULL = auto()
    BOOLEAN = auto()


_JSON_SCHEMA_TYPE_MAP: Tuple[Tuple[str, TypeEnum], ...] = (
    ("object", TypeEnum.OBJECT),
    ("array", TypeEnum.ARRAY),
    ("number", TypeEnum.NUMBER),
    ("integer", TypeEnum.INTEGER),
    ("string", TypeEnum.STRING),
    ("null", TypeEnum.NULL),
    ("boolean", TypeEnum.BOOLEAN),
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
    type_components: Iterator[TypeEnum] = (
        _TYPE_LOOKUP[type_] for type_ in types
    )
    return reduce(lambda x, y: x | y, type_components)


_ENUM_LOOKUP = {enum: keyword for keyword, enum in _JSON_SCHEMA_TYPE_MAP}


def get_type(flag: TypeEnum) -> Union[str, List[str]]:
    """Get jsonschema type representation of type flag."""
    return [_ENUM_LOOKUP[_flag] for _flag in _ENUM_LOOKUP if _flag & flag]
