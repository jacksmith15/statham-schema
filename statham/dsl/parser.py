from collections import defaultdict
import inspect
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
    schema = {key: _KEYWORD_MAPPER[key](value) for key, value in schema.items()}
    if "anyOf" in schema:
        return AnyOf(*(parse(sub_schema) for sub_schema in schema["anyOf"]))
    if "oneOf" in schema:
        return OneOf(*(parse(sub_schema) for sub_schema in schema["oneOf"]))
    if "type" not in schema:
        return Element()
    if isinstance(schema["type"], list):
        return AnyOf(
            *(parse({**schema, "type": type_}) for type_ in schema["type"])
        )
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
    }
    class_dict = ObjectClassDict(default=default, **properties)
    return ObjectMeta(schema["title"], (Object,), class_dict)
