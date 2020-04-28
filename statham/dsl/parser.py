# pylint: disable=too-many-lines
"""Parsing tools to convert JSON Schema dictionaries to DSL Element instances.

Some JSON Schema documents will be converted to an equivalent but structurally
differing representation. In particular, those that combine composition
keywords or use multiple types will be recomposed using ``"allOf"`` and
``"anyOf"`` respectively. See full docs for more
details.
"""
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


class _ParseState:
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
    """Parse a JSON Schema document to DSL Element format.

    Assumes references are already resolved, and that any ``"object"`` schemas
    or sub-schemas contain either a ``"title"`` annotation or an
    ``"_x_autotitle"`` annotation. See
    `json-ref-dict <https://pypi.org/project/json-ref-dict/0.6.0/>`_ for
    reference resolution and annotation tools.

    :return: A list of DSL elements, starting with the top level element,
        followed by each element in the top-level schema ``"definitions"``.
    """
    state = _ParseState()
    return [parse_element(schema, state)] + [
        parse_element(definition, state)
        for definition in schema.get("definitions", {}).values()
        if isinstance(definition, (dict, bool, Element))
    ]


@reraise(
    RecursionError,
    FeatureNotImplementedError,
    "Could not parse cyclical dependencies of this schema.",
)
def parse_element(
    schema: Union[bool, Dict[str, Any]], state: _ParseState = None
) -> Element:
    """Parse a single JSON Schema element to a DSL Element object.

    Called by :func:`parse` when parsing entire documents.

    >>> parse_element({"type": "string", "minLength": 3})
    String(minLength=3)

    :raises: :exc:`~statham.dsl.exceptions.FeatureNotImplementedError` if
        recursive cycles are detected.
    :raises: :exc:`statham.dsl.exceptions.SchemaParseError` if problems are
        found in the provided schema.
    :return: A single :class:`~statham.dsl.elements.Element` object equivalent
        to the schema described by :paramref:`parse_element.schema`.
    """
    if isinstance(schema, bool):
        return Element() if schema else Nothing()
    state = state or _ParseState()
    if isinstance(schema, Element):
        return schema
    if set(schema) & UNSUPPORTED_SCHEMA_KEYWORDS:
        raise FeatureNotImplementedError.unsupported_keywords(
            set(schema) & UNSUPPORTED_SCHEMA_KEYWORDS
        )
    for literal_key in ("default", "const", "enum"):
        if literal_key in schema:
            schema[literal_key] = _parse_literal(schema[literal_key])
    for keyword, parser in (
        ("properties", _parse_properties),
        ("items", _parse_items),
        ("patternProperties", _parse_pattern_properties),
        ("propertyNames", _parse_property_names),
        ("contains", _parse_contains),
        ("dependencies", _parse_dependencies),
    ):
        if keyword in schema:
            schema[keyword] = parser(schema, state)  # type: ignore
    schema["additionalProperties"] = _parse_additional_properties(schema, state)
    schema["additionalItems"] = _parse_additional_items(schema, state)
    if set(COMPOSITION_KEYWORDS) & set(schema):
        return _parse_composition(schema, state)
    if "type" not in schema:
        return Element(**_keyword_filter(Element)(schema))
    return _parse_typed(schema["type"], schema, state)


def _parse_literal(literal: Any) -> Any:
    """Parse literal values from schema.

    Keywords like `const`, `enum` and `default` refer to non-schema values.
    Annotations should be removed to prevent side effects.
    """
    if not isinstance(literal, (dict, list)):
        return literal
    if isinstance(literal, list):
        return [_parse_literal(val) for val in literal]
    return {
        key: _parse_literal(val)
        for key, val in literal.items()
        if key != "_x_autotitle"
    }


def _parse_contains(
    schema: Dict[str, Any], state: _ParseState = None
) -> Element:
    """Parse schema contains keyword."""
    state = state or _ParseState()
    return parse_element(schema["contains"], state)


def _parse_composition(
    schema: Dict[str, Any], state: _ParseState = None
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
    _parse_composition(schema) == AllOf(
        Integer(),
        OneOf(Element(minimum=3), Element(maximum=5)),
        AnyOf(Element(multipleOf=2), Element(multipleOf=3)),
    )
    ```
    """
    state = state or _ParseState()
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


def _parse_typed(
    type_value: Any, schema: Dict[str, Any], state: _ParseState = None
) -> Element:
    """Parse a typed schema with no composition keywords."""
    state = state or _ParseState()
    if not isinstance(type_value, (str, list)):
        raise SchemaParseError.invalid_type(type_value)
    if isinstance(type_value, list):
        return _parse_multi_typed(type_value, schema, state)
    if schema["type"] == "object":
        return _parse_object(schema, state)
    if schema["type"] == "array":
        return _parse_array(schema, state)
    element_type = _TYPE_MAPPING[type_value]
    sub_schema = _keyword_filter(element_type)(schema)
    return element_type(**sub_schema)


def _parse_multi_typed(
    type_list: List[str], schema: Dict[str, Any], state: _ParseState = None
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
    state = state or _ParseState()
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


def _parse_object(
    schema: Dict[str, Any], state: _ParseState = None
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
    :return: The ``Object`` model equivalent to the schema.
    """
    state = state or _ParseState()
    title = schema.get("title", schema.get("_x_autotitle"))
    if not title:
        raise SchemaParseError.missing_title(schema)
    title = _title_format(title)
    properties = schema.get("properties", {})
    properties.update(
        {
            _parse_attribute_name(key): _Property(
                Element(), required=True, source=key
            )
            for key in schema.get("required", [])
            if _parse_attribute_name(key) not in properties
        }
    )
    class_dict = ObjectClassDict()
    for key, value in properties.items():
        class_dict[key] = value
    cls_args = dict(additionalProperties=schema["additionalProperties"])
    for key in [
        "patternProperties",
        "minProperties",
        "maxProperties",
        "propertyNames",
        "dependencies",
        "const",
        "enum",
        "default",
    ]:
        if key in schema:
            cls_args[key] = schema[key]
    object_type = ObjectMeta(title, (Object,), class_dict, **cls_args)
    return state.dedupe(object_type)


def _parse_properties(
    schema: Dict[str, Any], state: _ParseState = None
) -> Dict[str, _Property]:
    """Parse properties from a schema element."""
    state = state or _ParseState()
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    return {
        **{
            _parse_attribute_name(key): _Property(
                parse_element(value, state),
                required=key in required,
                source=key,
            )
            for key, value in properties.items()
            # Ignore malformed values.
            if isinstance(value, (dict, bool))
        },
        **{
            _parse_attribute_name(key): prop
            for key, prop in properties.items()
            if isinstance(prop, _Property)
        },
    }


def _parse_attribute_name(name: str) -> str:
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
    if name[0] not in first_chars:
        name = f"_{name}"
    if name in RESERVED_PROPERTIES:
        name = f"{name}_"
    return name


def _parse_pattern_properties(
    schema: Dict[str, Any], state: _ParseState = None
) -> Dict[str, Element]:
    """Parse schema patternProperties keyword."""
    state = state or _ParseState()
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


def _parse_property_names(
    schema: Dict[str, Any], state: _ParseState = None
) -> Element:
    """Parse schema propertyNames keyword."""
    state = state or _ParseState()
    return parse_element(schema["propertyNames"], state)


def _parse_additional(
    key: str, schema: Dict[str, Any], state: _ParseState = None
) -> Union[Element, bool]:
    """Parse additional items or properties.

    Booleans are retained for these values, as they are more semantically
    meaningful than in general schemas.
    """
    state = state or _ParseState()
    additional = schema.get(key, True)
    if isinstance(additional, bool):
        return additional
    return parse_element(additional, state)


def _parse_additional_properties(
    schema: Dict[str, Any], state: _ParseState = None
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element.

    If key is not present, defaults to `True`.
    """
    return _parse_additional("additionalProperties", schema, state)


def _parse_additional_items(
    schema: Dict[str, Any], state: _ParseState = None
) -> Union[Element, bool]:
    """Parse additionalProperties from a schema element.

    If key is not present, defaults to `True`.
    """
    return _parse_additional("additionalItems", schema, state)


def _parse_array(schema: Dict[str, Any], state: _ParseState = None) -> Array:
    """Parse an array schema element."""
    state = state or _ParseState()
    items = schema.get("items", Element())
    return Array(**{**_keyword_filter(Array)(schema), "items": items})


def _parse_items(
    schema: Dict[str, Any], state: _ParseState = None
) -> Union[Element, List[Element]]:
    """Parse array items keyword to DSL Element.

    If not present, defaults to `Element()`.
    """
    state = state or _ParseState()
    items = schema.get("items", {})
    if isinstance(items, list):
        return [parse_element(item, state) for item in items]
    return parse_element(items, state)


def _parse_dependencies(
    schema: Dict[str, Any], state: _ParseState = None
) -> Dict[str, Union[List[str], Element]]:
    """Parse dependencies keyword from schema."""
    state = state or _ParseState()
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


def _keyword_filter(type_: Type) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
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
