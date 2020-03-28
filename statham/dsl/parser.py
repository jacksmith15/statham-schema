from collections import defaultdict
from functools import partial
import inspect
from itertools import chain
import re
from typing import Any, Callable, DefaultDict, Dict, Iterator, List, Type, Union

from statham.dsl.constants import NotPassed
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    CompositionElement,
    Integer,
    Null,
    Number,
    Object,
    ObjectOptions,
    OneOf,
    Element,
    String,
)
from statham.dsl.elements.meta import (
    ObjectClassDict,
    ObjectMeta,
    RESERVED_PROPERTIES,
)
from statham.dsl.exceptions import FeatureNotImplementedError, SchemaParseError
from statham.dsl.helpers import reraise
from statham.dsl.property import _Property


_TYPE_MAPPING = {
    "array": Array,
    "boolean": Boolean,
    "integer": Integer,
    "null": Null,
    "number": Number,
    "string": String,
}


def name_counter() -> DefaultDict[str, Iterator[int]]:
    def _iterator() -> Iterator[int]:
        cnt = 0
        while True:
            yield cnt
            cnt += 1

    dictionary: DefaultDict[str, Iterator[int]] = defaultdict(_iterator)
    _ = next(dictionary["0"])  # Ensure the dict is truthy
    return dictionary


def parse(schema: Dict[str, Any]) -> List[Element]:
    """Parse a JSONSchema document to DSL Element format.

    Checks the top-level and definitions keyword to collect elements.
    """
    counter: DefaultDict[str, Iterator[int]] = name_counter()
    # if "definitions" in schema:
    #     for key, value in schema["definitions"].copy().items():
    #         if isinstance(value, dict):
    #             schema["definitions"][key] = parse_element(value, counter)
    # schema["definitions"] = {
    #     key: parse_element(definition)
    #     for key, definition in schema.get("definitions", {}).items()
    #     if isinstance(definition, (dict, Element))
    # }

    return [parse_element(schema, counter)]
    #  + list(
    #     schema["definitions"].values()
    # )


@reraise(
    RecursionError,
    SchemaParseError,
    "Could not parse cyclical dependencies of this schema.",
)
def parse_element(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> Element:
    """Parse a JSONSchema element to a DSL Element object.

    Converts schemas with multiple type values to an equivalent
    representation using "anyOf". For example:
    ```
    {"type": ["string", "integer"]}
    ```
    becomes
    ```
    {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    ```
    """
    counter = counter or name_counter()
    if isinstance(schema, Element):
        return schema
    if "properties" in schema:
        schema["properties"] = parse_properties(schema, counter)
    if "items" in schema:
        schema["items"] = parse_items(schema, counter)
    schema["additionalProperties"] = parse_additional_properties(
        schema, counter
    )
    if {"anyOf", "oneOf"} & set(schema):
        return parse_composition(schema, counter)
    if "type" not in schema:
        return Element(**keyword_filter(Element)(schema))
    return parse_typed(schema["type"], schema, counter)


def parse_composition(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> CompositionElement:
    """Parse a schema with composition keywords."""
    counter = counter or name_counter()
    intersect = {"anyOf", "oneOf"} & set(schema)
    element_type: Type[CompositionElement]
    if intersect == {"anyOf"}:
        element_type = AnyOf
        sub_schemas = schema["anyOf"]
    elif intersect == {"oneOf"}:
        element_type = OneOf
        sub_schemas = schema["oneOf"]
    elif not intersect:
        raise ValueError(
            "Schema passed to `parse_composition` has no supported "
            "validation keywords."
        )
    else:
        raise FeatureNotImplementedError.multiple_composition_keywords()
    return element_type(
        *(parse_element(sub_schema, counter) for sub_schema in sub_schemas)
    )


def parse_typed(
    type_value: Any,
    schema: Dict[str, Any],
    counter: DefaultDict[str, Iterator[int]] = None,
) -> Element:
    """Parse a typed schema with no composition keywords."""
    if not isinstance(type_value, (str, list)):
        raise SchemaParseError.invalid_type(type_value)
    if isinstance(type_value, list):
        return parse_multi_typed(type_value, schema, counter)
    if schema["type"] == "object":
        return parse_object(schema, counter)
    if schema["type"] == "array":
        return parse_array(schema, counter)
    element_type = _TYPE_MAPPING[type_value]
    sub_schema = keyword_filter(element_type)(schema)
    return element_type(**sub_schema)


def parse_multi_typed(
    type_list: List[str],
    schema: Dict[str, Any],
    counter: DefaultDict[str, Iterator[int]] = None,
) -> CompositionElement:
    """Parse a schema with multiple type values."""
    counter = counter or name_counter()
    default = schema.get("default", NotPassed())
    schema = {key: val for key, val in schema.items() if key != "default"}
    if len(type_list) == 1:
        return parse_element({**schema, "type": type_list[0]}, counter)
    return AnyOf(
        *(
            parse_element({**schema, "type": type_value}, counter)
            for type_value in type_list
        ),
        default=default,
    )


def parse_object(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> ObjectMeta:
    """Parse an object schema element."""
    counter = counter or name_counter()
    title = schema.get("title", schema.get("_x_autotitle"))
    if not title:
        raise SchemaParseError.missing_title(schema)
    # title = _title_format(title)
    count = next(counter[title])
    if count:
        title = f"{title}_{count}"
    default = schema.get("default", NotPassed())
    properties = schema.get("properties", {})
    class_dict = ObjectClassDict(
        default=default,
        options=ObjectOptions(**keyword_filter(ObjectOptions)(schema)),
    )
    for key, value in properties.items():
        class_dict[key] = value
    return ObjectMeta(_title_format(title), (Object,), class_dict)


def parse_properties(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> Dict[str, _Property]:
    """Parse properties from a schema element."""
    required = set(schema.get("required", []))
    attr_name = lambda key: key if key not in RESERVED_PROPERTIES else f"_{key}"
    return {
        **{
            # TODO: Handle attribute names which don't work in python.
            attr_name(key): _Property(
                parse_element(value, counter),
                required=key in required,
                source=key,
            )
            for key, value in schema.get("properties", {}).items()
            # Ignore malformed values.
            if isinstance(value, dict)
        },
        **{
            attr_name(key): prop
            for key, prop in schema.get("properties", {}).items()
            if isinstance(prop, _Property)
        },
    }


def parse_additional_properties(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]]
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element."""
    counter = counter or name_counter()
    additional_properties = schema.get("additionalProperties", True)
    if isinstance(additional_properties, bool):
        return additional_properties
    return parse_element(additional_properties, counter)


def parse_array(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> Array:
    """Parse an array schema element."""
    counter = counter or name_counter()
    items = schema.get("items", Element())
    return Array(**{**keyword_filter(Array)(schema), "items": items})


def parse_items(
    schema: Dict[str, Any], counter: DefaultDict[str, Iterator[int]] = None
) -> Element:
    items = schema.get("items", {})
    if isinstance(items, list):
        raise FeatureNotImplementedError.tuple_array_items()
    return parse_element(items, counter)


def keyword_filter(type_: Type) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    params = inspect.signature(type_.__init__).parameters.values()
    args = {param.name for param in params}

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in schema.items() if key in args}

    return _filter


def _title_format(string: str) -> str:
    """Convert titles in schemas to class names."""
    words = list(filter(None, re.split(r"[ _-]", string)))
    segments = chain.from_iterable(
        [
            re.findall("[A-Z][^A-Z]*", word[0].upper() + word[1:])
            for word in words
        ]
    )
    return "".join(segment.title() for segment in segments)
