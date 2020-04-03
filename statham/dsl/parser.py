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
        if isinstance(definition, (dict, bool, Element))
    ]


@reraise(
    RecursionError,
    SchemaParseError,
    "Could not parse cyclical dependencies of this schema.",
)
def parse_element(
    schema: Union[bool, Dict[str, Any]], state: ParseState = None
) -> Element:
    """Parse a JSONSchema element to a DSL Element object."""
    if isinstance(schema, bool):
        return Element() if schema else Nothing()
    state = state or ParseState()
    if isinstance(schema, Element):
        return schema
    if set(schema) & UNSUPPORTED_SCHEMA_KEYWORDS:
        raise FeatureNotImplementedError.unsupported_keywords(
            set(schema) & UNSUPPORTED_SCHEMA_KEYWORDS
        )
    if "properties" in schema:
        schema["properties"] = parse_properties(schema, state)
    if "items" in schema:
        schema["items"] = parse_items(schema, state)
    if "patternProperties" in schema:
        schema["patternProperties"] = parse_pattern_properties(schema, state)
    schema["additionalProperties"] = parse_additional_properties(schema, state)
    schema["additionalItems"] = parse_additional_items(schema, state)
    if set(COMPOSITION_KEYWORDS) & set(schema):
        return parse_composition(schema, state)
    if "type" not in schema:
        return Element(**keyword_filter(Element)(schema))
    return parse_typed(schema["type"], schema, state)


def parse_composition(
    schema: Dict[str, Any], state: ParseState = None
) -> Element:
    """Parse a schema with composition keywords.

    Handles multiple composition keywords by wrapping them in an AllOf
    element. Similarly, non-keyword elements are parsed as usual and
    included in an allOf element.

    For example:
    ```python
    schema = {
        "type": "integer",
        "oneOf": [{"minimum": 3}, {"maximum": 5}],
        "anyOf": [{"multipleOf": 2}, {"multipleOf": 3}],
    }
    parse_composition(schema) == AllOf(
        Integer(),
        OneOf(Element(minimum=3), Element(maximum=5)),
        AnyOf(Element(multipleOf=2), Element(multipleOf=3)),
    )
    ```
    """
    state = state or ParseState()
    composition, other = split_dict(set(COMPOSITION_KEYWORDS) | {"default"})(
        schema
    )
    base_element = parse_element(other, state)
    for key in set(COMPOSITION_KEYWORDS) - {"not"}:
        composition[key] = [
            parse_element(sub_schema, state)
            for sub_schema in composition.get(key, [])
        ]
    all_of = [base_element] + composition["allOf"]
    all_of.append(_compose_elements(OneOf, composition["oneOf"]))
    all_of.append(_compose_elements(AnyOf, composition["anyOf"]))
    if "not" in composition:
        all_of.append(Not(parse_element(schema["not"], state)))
    element = _compose_elements(
        AllOf, filter(partial(op.ne, Element()), all_of)
    )
    default = schema.get("default", NotPassed())
    if isinstance(element, ObjectMeta):
        return AllOf(element, default=default)
    element.default = default or element.default
    return element


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
    properties.update(
        {
            parse_attribute_name(key): _Property(
                Element(), required=True, source=key
            )
            for key in schema.get("required", [])
            if parse_attribute_name(key) not in properties
        }
    )
    class_dict = ObjectClassDict(default=default)
    for key, value in properties.items():
        class_dict[key] = value
    cls_args = dict(additionalProperties=schema["additionalProperties"])
    if "patternProperties" in schema:
        cls_args["patternProperties"] = schema["patternProperties"]
    object_type = ObjectMeta(title, (Object,), class_dict, **cls_args)
    return state.dedupe(object_type)


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


def parse_additional(
    key: str, schema: Dict[str, Any], state: ParseState = None
) -> Union[Element, bool]:
    """Parse additional items or properties.

    Booleans are retained for these values, as they are more semantically
    meaningful than in general schemas.
    """
    state = state or ParseState()
    additional_properties = schema.get(key, True)
    if isinstance(additional_properties, bool):
        return additional_properties
    return parse_element(additional_properties, state)


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


def keyword_filter(type_: Type) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a filter to pull out only relevant keywords for a given type."""
    params = inspect.signature(type_.__init__).parameters.values()
    args = {param.name for param in params}

    def _filter(schema: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in schema.items() if key in args}

    return _filter


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
