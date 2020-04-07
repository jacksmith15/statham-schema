from collections import defaultdict
from functools import partial
import inspect
from itertools import chain
import operator as op
import re
import string
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Type,
    Union,
)
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
        self.seen_ids = {}


def parse_element(
    schema: Union[Dict[str, Any], bool], state: ParseState = None
) -> Element:
    state = state or ParseState()
    if isinstance(schema, bool):
        return {True: Element(), False: Nothing()}[schema]
    if id(schema) in state.seen_ids:
        return state.seen_ids[id(schema)]
    element = blank_element(schema)
    state.seen_ids[id(schema)] = element
    set_keyword_attributes(element, schema, state)
    # dedupe if object
    return element


def set_keyword_attributes(
    element: Element, schema: Dict[str, Any], state: ParseState
):
    """Set attributes on element based on schema.

    This is done as a post step to allow recursive references to be
    resolved once the instance is available in state.
    """
    if isinstance(element, (AllOf, AnyOf, Not, OneOf)):
        element.default = schema.get("default", NotPassed())
    if isinstance(element, Not):
        element.element = parse_element(schema["not"], state)
    elif isinstance(element, OneOf):
        element.elements = [
            parse_element(sub_schema, state) for sub_schema in schema["oneOf"]
        ]
    elif isinstance(element, AnyOf):
        if "anyOf" in schema:
            element.elements = [
                parse_element(sub_schema, state)
                for sub_schema in schema["anyOf"]
            ]
        elif isinstance(schema.get("type"), list):
            element.elements = [
                parse_element(
                    {**schema, "type": other_type, "default": NotPassed()},
                    state,
                )
                for other_type in schema["type"]
            ]
        else:
            raise ValueError(f"Got anyOf type for {schema}")
    elif isinstance(element, AllOf):
        composition, other = split_dict(
            set(COMPOSITION_KEYWORDS) | {"default"}
        )(schema)
        # This could cause infinite recursion?
        if isinstance(other.get("type"), list):
            base_element = _compose_elements(
                AnyOf,
                [
                    parse_element({**other, "type": other_type}, state)
                    for other_type in other["type"]
                ],
            )
        else:
            base_element = parse_element(other, state)
        composition_attrs = {
            "anyOf": [
                parse_element(sub_schema, state)
                for sub_schema in schema.get("anyOf", [])
            ],
            "oneOf": [
                parse_element(sub_schema, state)
                for sub_schema in schema.get("oneOf", [])
            ],
            "allOf": [
                parse_element(sub_schema, state)
                for sub_schema in schema.get("allOf", [])
            ],
        }
        all_of = [
            base_element,
            *composition_attrs["allOf"],
            _compose_elements(OneOf, composition_attrs["oneOf"]),
            _compose_elements(AnyOf, composition_attrs["anyOf"]),
        ]
        if "not" in composition:
            all_of.append(Not(parse_element(schema["not"], state)))
        dummy_element = _compose_elements(
            AllOf, filter(partial(op.ne, Element()), all_of)
        )
        if not isinstance(dummy_element, AllOf):
            element.elements = [dummy_element]
        else:
            element.elements = dummy_element.elements
    else:
        attrs = keyword_filter(type(element))(schema)
        if "required" in schema and "properties" not in attrs:
            attrs["properties"] = {}
        for key, value in keyword_filter(type(element))(schema).items():
            # more complex logic for composition
            if key in KEYWORD_PARSER:
                setattr(element, key, KEYWORD_PARSER[key](schema, state))
            else:
                setattr(element, key, value)


def blank_element(schema: Dict[str, Any]) -> Element:
    if is_composition(schema):
        return blank_composition_element(schema)
    if "type" not in schema:
        return Element()
    if not isinstance(schema["type"], (list, str)):
        raise SchemaParseError.invalid_type(schema["type"])
    schema_type: str
    if isinstance(schema["type"], list):
        if len(schema["type"]) > 1 or "default" in schema:
            return AnyOf(Element())
        schema_type = schema["type"][0]
    else:
        schema_type = schema["type"]
    title = schema.get("title", schema.get("_x_autotitle"))
    if schema_type == "object" and not title:
        raise SchemaParseError.missing_title(schema)
    formatted_title = _title_format(title) if title else "unknown"
    mapping: Dict[str, Element] = {
        "array": Array(Element()),
        "boolean": Boolean(),
        "null": Null(),
        "integer": Integer(),
        "number": Number(),
        "string": String(),
        "object": ObjectMeta(formatted_title, (Object,), ObjectClassDict()),
    }
    return mapping[schema_type]


def is_composition(schema: Dict[str, Any]) -> bool:
    composition: Set[str] = {
        key
        for key, value in schema.items()
        if key in set(COMPOSITION_KEYWORDS)
        and (value or not isinstance(value, list))
    }
    if not composition:
        return False
    return True


def blank_composition_element(schema: Dict[str, Any]) -> Element:
    """Get a blank element for schemas containing composition keywords.

    Outer keywords are an implicit allOf expression, and multiple
    composition keywords are implicitly combined as allOf expressions.

    In the DSL, we make those compositions explicit.
    """
    keys: Set[str] = set(schema)
    composition: Set[str] = keys & set(COMPOSITION_KEYWORDS)
    other: Set[str] = keys - set(COMPOSITION_KEYWORDS) - {"default"}
    if not composition:
        raise ValueError("No composition keywords in schema.")
    # If there are multiple compositions (including top-level), then they
    # will be combined in an AllOf.
    if other - {"default"} or "allOf" in composition or len(composition) > 1:
        return AllOf(Element())
    # There should be exactly 1 composition keyword now.
    keyword: str = next(iter(composition))
    return {
        "anyOf": AnyOf(Element()),
        "oneOf": OneOf(Element()),
        "not": Not(Nothing()),
    }[keyword]


Parser = Callable[[Dict[str, Any], Optional[ParseState]], Any]


def keyword_filter(type_: Type) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    if type_ is ObjectMeta:
        params = inspect.signature(type_.__new__).parameters.values()
        args = {
            param.name for param in params if param.kind == param.KEYWORD_ONLY
        } | {"properties"}
    else:
        params = inspect.signature(type_.__init__).parameters.values()
        args = {param.name for param in params}

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        if "required" in schema and "properties" not in schema:
            # Ensure properties are parsed if required is present.
            schema["properties"] = {}
        return {key: value for key, value in schema.items() if key in args}

    return _filter


def parse_literal(key: str) -> Parser:
    def _remove_annotations(literal):
        if not isinstance(literal, (dict, list)):
            return literal
        if isinstance(literal, list):
            return [_remove_annotations(val) for val in literal]
        return {
            key: _remove_annotations(val)
            for key, val in literal.items()
            if key != "_x_autotitle"
        }

    def _parse(schema: Dict[str, Any], _state: ParseState = None) -> Any:
        literal = schema.get(key, None)
        return _remove_annotations(literal)

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
        **{
            parse_attribute_name(key): _Property(
                Element(), required=True, source=key
            )
            for key in required
            if key not in properties
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


def _compose_elements(
    element_type: Type[CompositionElement], elements: Iterable[Element]
) -> Element:
    """Create a composition element from a type and list of component elements.

    Filters out trivial elements, and simplifies compositions with only one
    composed element.
    """
    elements = list(elements)
    if not elements:
        return Element()
    if len(elements) == 1:
        return elements[0]
    return element_type(*elements)


KEYWORD_PARSER: Dict[str, Parser] = {
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
