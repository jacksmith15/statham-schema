from collections import defaultdict
import inspect
from itertools import chain
import re
from typing import Any, Callable, DefaultDict, Dict, Type

from statham.dsl.constants import NotPassed
from statham.dsl.elements import AnyOf, Array, Object, OneOf, Element, String
from statham.dsl.elements.meta import ObjectClassDict, ObjectMeta
from statham.dsl.property import _Property


_TYPE_MAPPING = {"array": Array, "string": String}


_KEYWORD_MAPPER: DefaultDict[str, Callable] = defaultdict(
    lambda: lambda val: val
)


def parse(schema: Dict[str, Any]) -> Element:
    """Parse a JSONSchema dictionary to a DSL Element."""
    if isinstance(schema.get("type"), list):
        return AnyOf(
            *(parse({**schema, "type": type_}) for type_ in schema["type"])
        )
    schema = {key: _KEYWORD_MAPPER[key](value) for key, value in schema.items()}
    if "anyOf" in schema:
        return AnyOf(*(parse(sub_schema) for sub_schema in schema["anyOf"]))
    if "oneOf" in schema:
        return OneOf(*(parse(sub_schema) for sub_schema in schema["oneOf"]))
    if "type" not in schema:
        return Element()
    if schema["type"] == "object":
        return _new_object(schema)

    elem_cls = _TYPE_MAPPING[schema["type"]]
    sub_schema = _args_filter(elem_cls)(schema)
    return elem_cls(**sub_schema)


_KEYWORD_MAPPER["items"] = parse


def _args_filter(
    elem_cls: Type[Element]
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    params = inspect.signature(elem_cls.__init__).parameters.values()
    args = {param.name for param in params}

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in schema.items() if key in args}

    return _filter


def _new_object(schema: Dict[str, Any]) -> ObjectMeta:
    default = schema.get("default", NotPassed())
    required = set(schema.get("required", []))
    properties = {
        key: _Property(parse(value), required=key in required)
        for key, value in schema.get("properties", {}).items()
        # Ignore autogenerated context labelling.
        if isinstance(value, dict)
    }
    class_dict = ObjectClassDict(default=default, **properties)
    title = _title_format(schema.get("title", schema.get("_x_autotitle")))
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
