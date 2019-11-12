from enum import Enum, unique
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
class TypeEnum(Enum):
    OBJECT = "object"
    ARRAY = "array"
    NUMBER = "number"
    INTEGER = "integer"
    STRING = "string"
    NULL = "null"
