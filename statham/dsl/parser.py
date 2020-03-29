from collections import defaultdict
import inspect
from itertools import chain
import re
from typing import Any, Callable, DefaultDict, Dict, List, Type, Union

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


class ParseState:
    """Recusive state.

    Used to de-duplicate models which are traversed multiple times, and to
    rename distinct models with the same name.
    """

    def __init__(self):
        self.seen: DefaultDict[str, List[ObjectMeta]] = defaultdict(list)

    def dedupe(self, object_type: ObjectMeta):
        """Deduplicate a parsed model.

        If it has been seen before, then return the existing one. Otherwise
        ensure the model's name is distinct from other models and keep store
        it.
        """
        name = object_type.__name__
        for existing in self.seen[name]:
            if object_type == existing:
                return existing
        count = len(self.seen[name])
        if count:
            object_type.__name__ = name + f"_{count}"
        self.seen[name].append(object_type)
        return object_type


def parse(schema: Dict[str, Any]) -> List[Element]:
    """Parse a JSONSchema document to DSL Element format.

    Checks the top-level and definitions keyword to collect elements.
    """
    state = ParseState()
    return [parse_element(schema, state)] + [
        parse_element(definition, state)
        for definition in schema.get("definitions", {}).values()
        if isinstance(definition, (dict, Element))
    ]


@reraise(
    RecursionError,
    SchemaParseError,
    "Could not parse cyclical dependencies of this schema.",
)
def parse_element(schema: Dict[str, Any], state: ParseState = None) -> Element:
    """Parse a JSONSchema element to a DSL Element object."""
    state = state or ParseState()
    if isinstance(schema, Element):
        return schema
    if "properties" in schema:
        schema["properties"] = parse_properties(schema, state)
    if "items" in schema:
        schema["items"] = parse_items(schema, state)
    schema["additionalProperties"] = parse_additional_properties(schema, state)
    if {"anyOf", "oneOf"} & set(schema):
        return parse_composition(schema, state)
    if "type" not in schema:
        return Element(**keyword_filter(Element)(schema))
    return parse_typed(schema["type"], schema, state)


def parse_composition(
    schema: Dict[str, Any], state: ParseState = None
) -> CompositionElement:
    """Parse a schema with composition keywords.

    :raises ValueError: if the schema does not contain any composition
        keywords.
    :raises FeatureNotImplementedError: if multiple composition keywords
        are present.
    """
    state = state or ParseState()
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
        *(parse_element(sub_schema, state) for sub_schema in sub_schemas)
    )


def parse_typed(
    type_value: Any, schema: Dict[str, Any], state: ParseState = None
) -> Element:
    """Parse a typed schema with no composition keywords.

    :raises KeyError: if no "type" key is present.
    :raises SchemaParseError: if value at "type" is not a `str` or `list`.
    """
    state = state or ParseState()
    if not isinstance(type_value, (str, list)):
        raise SchemaParseError.invalid_type(type_value)
    if isinstance(type_value, list):
        return parse_multi_typed(type_value, schema, state)
    if schema["type"] == "object":
        return parse_object(schema, state)
    if schema["type"] == "array":
        return parse_array(schema, state)
    element_type = _TYPE_MAPPING[type_value]
    sub_schema = keyword_filter(element_type)(schema)
    return element_type(**sub_schema)


def parse_multi_typed(
    type_list: List[str], schema: Dict[str, Any], state: ParseState = None
) -> CompositionElement:
    """Parse a schema with multiple type values.

    Converts schema to an equivalent representation using "anyOf". For example:
    ```python
    {"type": ["string", "integer"]}
    ```
    becomes
    ```
    {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    ```
    """
    state = state or ParseState()
    default = schema.get("default", NotPassed())
    schema = {key: val for key, val in schema.items() if key != "default"}
    if len(type_list) == 1:
        return parse_element({**schema, "type": type_list[0]}, state)
    return AnyOf(
        *(
            parse_element({**schema, "type": type_value}, state)
            for type_value in type_list
        ),
        default=default,
    )


def parse_object(
    schema: Dict[str, Any], state: ParseState = None
) -> ObjectMeta:
    """Parse an object schema element to an `Object` subclass.

    The name of the generated class is derived from the following keys
    in precedence order:
    - "title"
    - "_x_autotitle"

    Also requires that "properties" and "additionalProperties" values have
    already been parsed.

    :raises SchemaParseError: if keys exist from which to derive the class
        title.
    """
    state = state or ParseState()
    title = schema.get("title", schema.get("_x_autotitle"))
    if not title:
        raise SchemaParseError.missing_title(schema)
    title = _title_format(title)
    default = schema.get("default", NotPassed())
    properties = schema.get("properties", {})
    class_dict = ObjectClassDict(
        default=default,
        options=ObjectOptions(**keyword_filter(ObjectOptions)(schema)),
    )
    for key, value in properties.items():
        class_dict[key] = value
    object_type = ObjectMeta(title, (Object,), class_dict)
    return state.dedupe(object_type)


def parse_properties(
    schema: Dict[str, Any], state: ParseState = None
) -> Dict[str, _Property]:
    """Parse properties from a schema element."""
    state = state or ParseState()
    required = set(schema.get("required", []))
    attr_name = lambda key: key if key not in RESERVED_PROPERTIES else f"_{key}"
    return {
        **{
            # TODO: Handle attribute names which don't work in python.
            attr_name(key): _Property(
                parse_element(value, state),
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
    schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element.

    If key is not present, defaults to `True`.
    """
    state = state or ParseState()
    additional_properties = schema.get("additionalProperties", True)
    if isinstance(additional_properties, bool):
        return additional_properties
    return parse_element(additional_properties, state)


def parse_array(schema: Dict[str, Any], state: ParseState = None) -> Array:
    """Parse an array schema element."""
    state = state or ParseState()
    items = schema.get("items", Element())
    return Array(**{**keyword_filter(Array)(schema), "items": items})


def parse_items(schema: Dict[str, Any], state: ParseState = None) -> Element:
    """Parse array items keyword to DSL Element.

    If not present, defaults to `Element()`.
    """
    state = state or ParseState()
    items = schema.get("items", {})
    if isinstance(items, list):
        raise FeatureNotImplementedError.tuple_array_items()
    return parse_element(items, state)


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
