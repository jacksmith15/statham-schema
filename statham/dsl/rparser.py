from collections import defaultdict
from functools import partial
import inspect
from itertools import chain
import operator as op
import re
import string
from typing import Any, Callable, DefaultDict, Dict, Iterable, List, Type, Union
import unicodedata

from statham.dsl.constants import (
    COMPOSITION_KEYWORDS,
    NotPassed,
    UNSUPPORTED_SCHEMA_KEYWORDS,
)
from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    Boolean,
    CompositionElement,
    Integer,
    Not,
    Nothing,
    Null,
    Number,
    Object,
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
from statham.dsl.helpers import expand, reraise, split_dict
from statham.dsl.property import _Property


class ParseState:
    """Recusive state.

    Used to de-duplicate models which are traversed multiple times, and to
    rename distinct models with the same name.
    """

    def __init__(self):
        self.seen: DefaultDict[str, List[ObjectMeta]] = defaultdict(list)
        self.seen_ids = {}

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


def parse_element(schema, state=None):
    state = state or ParseState()
    if id(schema) in state.seen_ids:
        return state.seen_ids[id(schema)]
    element = blank_element(schema)
    state.seen_ids[id(schema)] = element
    for key, value in keyword_filter(type(element))(schema).items():
        if key in KEYWORD_PARSER:
            setattr(element, key, KEYWORD_PARSER[key](schema, state))
        else:
            setattr(element, key, value)
    return element


def blank_element(schema):
    if "type" not in schema:
        return Element()
    return {
        "array": Array(Element()),
        "boolean": Boolean(),
        "null": Null(),
        "integer": Integer(),
        "number": Number(),
        "string": String(),
        "object": ObjectMeta(
            schema.get("title", "unknown"), (Object,), ObjectClassDict()
        ),
    }[schema["type"]]


def keyword_filter(type_: Type) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    params = inspect.signature(type_.__init__).parameters.values()
    args = {param.name for param in params}
    if type_ is ObjectMeta:
        args = {
            "default",
            "const",
            "enum",
            "properties",
            "minProperties",
            "maxProperties",
            "patternProperties",
            "additionalProperties",
        }

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in schema.items() if key in args}

    return _filter


def parse_literal(key):
    def _parse(schema, state=None):
        literal = schema.get(key, None)
        if not isinstance(literal, (dict, list)):
            return literal
        if isinstance(literal, list):
            return [parse_literal(val) for val in literal]
        return {
            key: parse_literal(val)
            for key, val in literal.items()
            if key != "_x_autotitle"
        }

    return _parse


def parse_contains(schema: Dict[str, Any], state: ParseState = None) -> Element:
    """Parse schema contains keyword."""
    state = state or ParseState()
    return parse_element(schema["contains"], state)


def parse_properties(
    schema: Dict[str, Any], state: ParseState = None
) -> Dict[str, _Property]:
    """Parse properties from a schema element."""
    state = state or ParseState()
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    return {
        **{
            parse_attribute_name(key): _Property(
                parse_element(value, state),
                required=key in required,
                source=key,
            )
            for key, value in properties.items()
            # Ignore malformed values.
            if isinstance(value, (dict, bool))
        },
        **{
            parse_attribute_name(key): prop
            for key, prop in properties.items()
            if isinstance(prop, _Property)
        },
    }


def parse_attribute_name(name: str) -> str:
    """Convert attibute name to valid python attribute.

    Attempts to replace special characters with their unicode names.
    """

    def _char_map(idx: int, char: str) -> str:
        if char.isalnum() or char in ("_", "-", " "):
            return char
        if char in string.whitespace:
            return "_"
        label = unicodedata.name(char, "unknown").lower()
        if idx != 0 and name[idx - 1] != "_":
            label = "_" + label
        if idx != len(name) - 1 and name[idx + 1] != "_":
            label = label + "_"
        return label

    chars = map(expand(_char_map), enumerate(name))
    name = "".join(chars).replace(" ", "_").replace("-", "_")
    if not name:
        return "blank"
    first_chars = set(string.ascii_letters) | {"_"}
    return (
        name
        if name not in RESERVED_PROPERTIES and name[0] in first_chars
        else f"_{name}"
    )


def parse_pattern_properties(
    schema: Dict[str, Any], state: ParseState = None
) -> Dict[str, Element]:
    """Parse schema patternProperties keyword."""
    state = state or ParseState()
    return {
        **{
            key: parse_element(value, state)
            for key, value in schema["patternProperties"].items()
            if isinstance(value, (dict, bool))
        },
        **{
            key: value
            for key, value in schema["patternProperties"].items()
            if isinstance(value, Element)
        },
    }


def parse_property_names(
    schema: Dict[str, Any], state: ParseState = None
) -> Element:
    """Parse schema propertyNames keyword."""
    state = state or ParseState()
    return parse_element(schema["propertyNames"], state)


def parse_additional(
    key: str, schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, bool]:
    """Parse additional items or properties.

    Booleans are retained for these values, as they are more semantically
    meaningful than in general schemas.
    """
    state = state or ParseState()
    additional = schema.get(key, True)
    if isinstance(additional, bool):
        return additional
    return parse_element(additional, state)


def parse_additional_properties(
    schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element.

    If key is not present, defaults to `True`.
    """
    return parse_additional("additionalProperties", schema, state)


def parse_additional_items(
    schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element.

    If key is not present, defaults to `True`.
    """
    return parse_additional("additionalItems", schema, state)


def parse_array(schema: Dict[str, Any], state: ParseState = None) -> Array:
    """Parse an array schema element."""
    state = state or ParseState()
    items = schema.get("items", Element())
    return Array(**{**keyword_filter(Array)(schema), "items": items})


def parse_items(
    schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, List[Element]]:
    """Parse array items keyword to DSL Element.

    If not present, defaults to `Element()`.
    """
    state = state or ParseState()
    items = schema.get("items", {})
    if isinstance(items, list):
        return [parse_element(item, state) for item in items]
    return parse_element(items, state)


def parse_dependencies(
    schema: Dict[str, Any], state: ParseState = None
) -> Dict[str, Union[List[str], Element]]:
    """Parse dependencies keyword from schema."""
    state = state or ParseState()
    return {
        **{
            key: value
            for key, value in schema["dependencies"].items()
            if isinstance(value, (list, Element))
        },
        **{
            key: parse_element(value, state)
            for key, value in schema["dependencies"].items()
            if isinstance(value, (dict, bool))
        },
    }


def _title_format(name: str) -> str:
    """Convert titles in schemas to class names."""
    words = list(filter(None, re.split(r"[ _-]", name)))
    segments = chain.from_iterable(
        [
            re.findall("[A-Z][^A-Z]*", word[0].upper() + word[1:])
            for word in words
        ]
    )
    return "".join(segment.title() for segment in segments)


KEYWORD_PARSER = {
    "properties": parse_properties,
    "items": parse_items,
    "patternProperties": parse_pattern_properties,
    "propertyNames": parse_property_names,
    "contains": parse_contains,
    "dependencies": parse_dependencies,
    "additionalProperties": parse_additional_properties,
    "additionalItems": parse_additional_items,
    "default": parse_literal("default"),
    "const": parse_literal("const"),
    "enum": parse_literal("enum"),
}
