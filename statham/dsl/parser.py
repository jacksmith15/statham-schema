import inspect
from itertools import chain
import re
from typing import Any, Callable, Dict, Type

from statham.dsl.constants import NotPassed
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Integer,
    Null,
    Number,
    Object,
    OneOf,
    Element,
    String,
)
from statham.dsl.elements.meta import ObjectClassDict, ObjectMeta
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.property import _Property


_TYPE_MAPPING = {
    "array": Array,
    "boolean": Boolean,
    "integer": Integer,
    "null": Null,
    "number": Number,
    "string": String,
}


def parse(schema: Dict[str, Any]) -> Element:
    """Parse a JSONSchema dictionary to a DSL Element object.

    Converts schemas with multiple type values to an equivalent
    representation using "anyOf". For example:
    ```
    {"type": ["string", "integer"]}
    ```
    becomes
    ```
    {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    ```
    # TODO: definitions
    """
    if isinstance(schema.get("type"), list):
        default = schema.pop("default", NotPassed())
        return AnyOf(
            *(parse({**schema, "type": type_}) for type_ in schema["type"]),
            default=default,
        )
    if "anyOf" in schema:
        return AnyOf(*(parse(sub_schema) for sub_schema in schema["anyOf"]))
    if "oneOf" in schema:
        return OneOf(*(parse(sub_schema) for sub_schema in schema["oneOf"]))
    if "type" not in schema:
        return Element()
    if schema["type"] == "array":
        schema["items"] = parse(schema.get("items", {}))
    if schema["type"] == "object":
        return _new_object(schema)

    element_type = _TYPE_MAPPING[schema["type"]]
    sub_schema = keyword_filter(element_type)(schema)
    return element_type(**sub_schema)


def keyword_filter(
    elem_cls: Type[Element]
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    params = inspect.signature(elem_cls.__init__).parameters.values()
    args = {param.name for param in params}

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in schema.items() if key in args}

    return _filter


def _new_object(schema: Dict[str, Any]) -> ObjectMeta:
    """Create a new model type for an object schema."""
    default = schema.get("default", NotPassed())
    required = set(schema.get("required", []))
    properties = {
        # TODO: Handle attribute names which don't work in python.
        key: _Property(parse(value), required=key in required)
        for key, value in schema.get("properties", {}).items()
        # Ignore malformed values.
        if isinstance(value, dict)
    }
    class_dict = ObjectClassDict(default=default, **properties)
    title = _title_format(schema.get("title", schema.get("_x_autotitle")))
    if not title:
        raise SchemaParseError.missing_title(schema)
    return ObjectMeta(title, (Object,), class_dict)


def _title_format(string: str) -> str:
    """Convert titles in schemas to class names."""
    words = re.split(r"[ _-]", string)
    segments = chain.from_iterable(
        [
            re.findall("[A-Z][^A-Z]*", word[0].upper() + word[1:])
            for word in words
        ]
    )
    return "".join(segment.title() for segment in segments)
