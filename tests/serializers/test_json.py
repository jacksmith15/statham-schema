from itertools import chain
from typing import Any, Callable, Dict, List, Tuple

import pytest

from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    Boolean,
    Element,
    Integer,
    Not,
    Nothing,
    Null,
    Number,
    Object,
    OneOf,
    String,
)
from statham.dsl.property import Property, _Property
from statham.serializers.json import serialize_element, serialize_json
from tests.dsl.parser.test_parse_object import (
    EmptyModel,
    ObjectWithOptionalProperty,
    ObjectWithRequiredProperty,
    ObjectWithObjectProperty,
    ObjectWithDefaultProp,
    ObjectWithAdditionalPropElement,
    ObjectWithAdditionalPropTrue,
    ObjectWithAdditionalPropFalse,
    ObjectWithPatternProps,
    ObjectWithSizeValidation,
    ObjectWithPropertyNames,
    ObjectWithConst,
    ObjectWithEnum,
    ObjectWithDependencies,
)
from tests.models.multi_object import Model


lcat: Callable = lambda x: list(chain.from_iterable(x))


ParamSet = List[Tuple[Element, Any]]


ARRAY_PARAMS: ParamSet = [
    (Array(Element()), {"type": "array", "items": {}}),
    (Array(String()), {"type": "array", "items": {"type": "string"}}),
    (
        Array(
            String(),
            default=["foo", "bar"],
            minItems=1,
            maxItems=3,
            contains=String(),
            uniqueItems=True,
        ),
        {
            "type": "array",
            "items": {"type": "string"},
            "default": ["foo", "bar"],
            "minItems": 1,
            "maxItems": 3,
            "contains": {"type": "string"},
            "uniqueItems": True,
        },
    ),
    (
        Array(
            [String(), Integer()],
            default=["foo", 1],
            minItems=2,
            additionalItems=False,
        ),
        {
            "type": "array",
            "items": [{"type": "string"}, {"type": "integer"}],
            "default": ["foo", 1],
            "minItems": 2,
            "additionalItems": False,
        },
    ),
]


BOOLEAN_PARAMS: ParamSet = [
    (Boolean(), {"type": "boolean"}),
    (Boolean(default=True), {"type": "boolean", "default": True}),
]


COMPOSITION_PARAMS: ParamSet = lcat(
    [
        (elem(String()), {keyword: [{"type": "string"}]}),
        (
            elem(String(), default="sample string"),
            {keyword: [{"type": "string"}], "default": "sample string"},
        ),
        (
            elem(String(), Array(String())),
            {
                keyword: [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ]
            },
        ),
        (
            elem(String(), Array(String()), default="sample string"),
            {
                keyword: [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ],
                "default": "sample string",
            },
        ),
    ]
    for elem, keyword in ((AnyOf, "anyOf"), (AllOf, "allOf"), (OneOf, "oneOf"))
)


ELEMENT_PARAMS: ParamSet = [
    (Element(), {}),
    (Element(minLength=3), {"minLength": 3}),
    (
        Element(
            default="foo",
            const="foo",
            minItems=3,
            maxItems=5,
            minimum=3,
            maximum=5,
            minLength=3,
            maxLength=5,
            required=["value"],
            properties={"value": _Property(String(), required=True)},
            additionalProperties=String(),
            patternProperties={"^foo": String()},
            minProperties=1,
            maxProperties=3,
            items=String(),
            uniqueItems=True,
            propertyNames=String(maxLength=3),
            contains=String(),
            enum=["foo", "bar"],
            dependencies={"foo": ["bar"], "qux": Element(minProperties=2)},
        ),
        {
            "default": "foo",
            "const": "foo",
            "minItems": 3,
            "maxItems": 5,
            "minimum": 3,
            "maximum": 5,
            "minLength": 3,
            "maxLength": 5,
            "required": ["value"],
            "properties": {"value": {"type": "string"}},
            "additionalProperties": {"type": "string"},
            "patternProperties": {"^foo": {"type": "string"}},
            "minProperties": 1,
            "maxProperties": 3,
            "items": {"type": "string"},
            "uniqueItems": True,
            "propertyNames": {"type": "string", "maxLength": 3},
            "contains": {"type": "string"},
            "enum": ["foo", "bar"],
            "dependencies": {"foo": ["bar"], "qux": {"minProperties": 2}},
        },
    ),
]

NOT_PARAMS: ParamSet = [
    (Not(Element()), {"not": {}}),
    (Not(String()), {"not": {"type": "string"}}),
]


NULL_PARAMS: ParamSet = [
    (Null(), {"type": "null"}),
    (Null(default=None), {"type": "null", "default": None}),
]


NUMERIC_PARAMS: ParamSet = [
    (Integer(), {"type": "integer"}),
    (
        Integer(
            default=4,
            minimum=2,
            exclusiveMinimum=2,
            maximum=7,
            exclusiveMaximum=7,
            multipleOf=2,
        ),
        {
            "type": "integer",
            "default": 4,
            "minimum": 2,
            "exclusiveMinimum": 2,
            "maximum": 7,
            "exclusiveMaximum": 7,
            "multipleOf": 2,
        },
    ),
    (Number(), {"type": "number"}),
    (
        Number(
            default=4,
            minimum=2,
            exclusiveMinimum=2,
            maximum=7,
            exclusiveMaximum=7,
            multipleOf=2,
        ),
        {
            "type": "number",
            "default": 4,
            "minimum": 2,
            "exclusiveMinimum": 2,
            "maximum": 7,
            "exclusiveMaximum": 7,
            "multipleOf": 2,
        },
    ),
]


OBJECT_PARAMS: ParamSet = [
    (EmptyModel, {"type": "object", "title": "EmptyModel"}),
    (
        ObjectWithOptionalProperty,
        {
            "type": "object",
            "title": "ObjectWithOptionalProperty",
            "properties": {"value": {"type": "string"}},
        },
    ),
    (
        ObjectWithRequiredProperty,
        {
            "type": "object",
            "title": "ObjectWithRequiredProperty",
            "required": ["value"],
            "properties": {"value": {"type": "string"}},
        },
    ),
    (
        ObjectWithObjectProperty,
        {
            "type": "object",
            "title": "ObjectWithObjectProperty",
            "required": ["value"],
            "properties": {
                "value": {
                    "type": "object",
                    "title": "ObjectWithRequiredProperty",
                    "required": ["value"],
                    "properties": {"value": {"type": "string"}},
                }
            },
        },
    ),
    (
        ObjectWithDefaultProp,
        {
            "type": "object",
            "title": "ObjectWithDefaultProp",
            "default": {"default": "a string"},
            "properties": {"value": {"type": "string"}},
        },
    ),
    (
        ObjectWithAdditionalPropElement,
        {
            "type": "object",
            "title": "ObjectWithAdditionalPropElement",
            "additionalProperties": {"type": "string"},
        },
    ),
    (
        ObjectWithAdditionalPropTrue,
        {"type": "object", "title": "ObjectWithAdditionalPropTrue"},
    ),
    (
        ObjectWithAdditionalPropFalse,
        {
            "type": "object",
            "title": "ObjectWithAdditionalPropFalse",
            "additionalProperties": False,
        },
    ),
    (
        ObjectWithPatternProps,
        {
            "type": "object",
            "title": "ObjectWithPatternProps",
            "patternProperties": {"^foo": {}, "^(?!foo)": False},
        },
    ),
    (
        ObjectWithSizeValidation,
        {
            "type": "object",
            "title": "ObjectWithSizeValidation",
            "minProperties": 1,
            "maxProperties": 2,
        },
    ),
    (
        ObjectWithPropertyNames,
        {
            "type": "object",
            "title": "ObjectWithPropertyNames",
            "propertyNames": {"type": "string", "maxLength": 3},
        },
    ),
    (
        ObjectWithConst,
        {"type": "object", "title": "ObjectWithConst", "const": {"foo": "bar"}},
    ),
    (
        ObjectWithEnum,
        {
            "type": "object",
            "title": "ObjectWithEnum",
            "enum": [{"foo": "bar"}, {"qux": "mux"}],
        },
    ),
    (
        ObjectWithDependencies,
        {
            "type": "object",
            "title": "ObjectWithDependencies",
            "dependencies": {"foo": ["bar"], "qux": {"minProperties": 2}},
        },
    ),
]


STRING_PARAMS: ParamSet = [
    (String(), {"type": "string"}),
    (
        String(
            default="sample",
            format="my_format",
            pattern=".*",
            minLength=1,
            maxLength=3,
        ),
        {
            "type": "string",
            "default": "sample",
            "format": "my_format",
            "pattern": ".*",
            "minLength": 1,
            "maxLength": 3,
        },
    ),
]


@pytest.mark.parametrize(
    "element,expected",
    (
        ARRAY_PARAMS
        + BOOLEAN_PARAMS
        + COMPOSITION_PARAMS
        + ELEMENT_PARAMS
        + NOT_PARAMS
        + NULL_PARAMS
        + NUMERIC_PARAMS
        + OBJECT_PARAMS
        + STRING_PARAMS
    ),
    ids=lambda element: repr(element) if isinstance(element, Element) else None,
)
def test_serialize_element(element: Element, expected: Dict[str, Any]):
    assert serialize_element(element) == expected


@pytest.mark.parametrize(
    "elements,expected",
    [
        (
            [Model],
            {
                "title": "Model",
                "type": "object",
                "properties": {
                    "children": {
                        "type": "array",
                        "items": "#/definitions/Child",
                    },
                    "category": "#/definitions/Category",
                },
                "definitions": {
                    "Child": {
                        "properties": {
                            "name": {"type": "string"},
                            "category": "#/definitions/Category",
                        },
                        "title": "Child",
                        "type": "object",
                    },
                    "Category": {
                        "properties": {"required_name": {"type": "string"}},
                        "required": ["required_name"],
                        "title": "Category",
                        "type": "object",
                    },
                },
            },
        ),
        ([String()], {"type": "string"}),
        (
            [Array(String()), ObjectWithOptionalProperty],
            {
                "type": "array",
                "items": {"type": "string"},
                "definitions": {
                    "ObjectWithOptionalProperty": {
                        "type": "object",
                        "title": "ObjectWithOptionalProperty",
                        "properties": {"value": {"type": "string"}},
                    }
                },
            },
        ),
    ],
)
def test_serialize_json(elements, expected):
    assert serialize_json(*elements) == expected
