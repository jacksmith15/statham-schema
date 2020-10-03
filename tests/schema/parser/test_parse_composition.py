from typing import Any, Dict

import pytest

from statham.schema.elements import (
    AllOf,
    AnyOf,
    Array,
    Element,
    Integer,
    Not,
    Number,
    Object,
    OneOf,
    String,
)
from statham.schema.exceptions import ValidationError
from statham.schema.parser import parse_element
from statham.schema.property import Property
from tests.helpers import no_raise


@pytest.mark.parametrize("keyword", ["anyOf", "oneOf", "allOf"])
def test_parse_composition_with_empty_list(keyword):
    schema = {keyword: []}
    assert parse_element(schema) == Element()


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param({"not": {}}, Not(Element()), id="not-with-blank-element"),
        pytest.param(
            {"not": {"type": "string"}},
            Not(String()),
            id="not-with-typed-element",
        ),
        pytest.param(
            {"anyOf": [{"type": "string"}]},
            String(),
            id="anyOf-with-one-sub-element",
        ),
        pytest.param(
            {"anyOf": [{"type": "string"}], "default": "sample string"},
            String(default="sample string"),
            id="anyOf-with-one-sub-element-and-default",
        ),
        pytest.param(
            {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ]
            },
            AnyOf(String(), Array(String())),
            id="anyOf-with-multiple-sub-elements",
        ),
        pytest.param(
            {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ],
                "default": "sample string",
            },
            AnyOf(String(), Array(String()), default="sample string"),
            id="anyOf-with-multiple-sub-elements-and-default",
        ),
        pytest.param(
            {"type": "string", "anyOf": [{"minLength": 3}]},
            AllOf(String(), Element(minLength=3)),
            id="anyOf-with-one-sub-element-and-outer-type",
        ),
        pytest.param(
            {"type": "string", "anyOf": [{"minLength": 3}, {"maxLength": 5}]},
            AllOf(String(), AnyOf(Element(minLength=3), Element(maxLength=5))),
            id="anyOf-with-multiple-sub-elements-and-outer-type",
        ),
        pytest.param(
            {
                "type": ["string", "array"],
                "minLength": 3,
                "minItems": 3,
                "items": {"type": "string", "maxLength": 1},
            },
            AnyOf(String(minLength=3), Array(String(maxLength=1), minItems=3)),
            id="anyOf-from-multiple-type-value",
        ),
        pytest.param(
            {"type": ["string", "integer"], "default": "sample"},
            AnyOf(String(), Integer(), default="sample"),
            id="anyOf-from-multiple-type-value-with-typed-default",
        ),
        pytest.param(
            {"oneOf": [{"type": "string"}]},
            String(),
            id="oneOf-with-one-sub-element",
        ),
        pytest.param(
            {"oneOf": [{"type": "string"}], "default": "sample string"},
            String(default="sample string"),
            id="oneOf-with-one-sub-element-and-default",
        ),
        pytest.param(
            {
                "oneOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ]
            },
            OneOf(String(), Array(String())),
            id="oneOf-with-multiple-sub-elements",
        ),
        pytest.param(
            {
                "oneOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ],
                "default": "sample string",
            },
            OneOf(String(), Array(String()), default="sample string"),
            id="oneOf-with-multiple-sub-elements-and-default",
        ),
        pytest.param(
            {"type": "string", "oneOf": [{"minLength": 3}]},
            AllOf(String(), Element(minLength=3)),
            id="oneOf-with-one-sub-element-and-outer-type",
        ),
        pytest.param(
            {"type": "string", "oneOf": [{"minLength": 3}, {"maxLength": 5}]},
            AllOf(String(), OneOf(Element(minLength=3), Element(maxLength=5))),
            id="oneOf-with-multiple-sub-elements-and-outer-type",
        ),
        pytest.param(
            {"allOf": [{"type": "string"}]},
            String(),
            id="allOf-with-one-sub-element",
        ),
        pytest.param(
            {"allOf": [{"type": "string"}], "default": "sample string"},
            String(default="sample string"),
            id="allOf-with-one-sub-element-and-default",
        ),
        pytest.param(
            {"allOf": [{"type": "string"}, {"minLength": 3}]},
            AllOf(String(), Element(minLength=3)),
            id="allOf-with-multiple-sub-elements",
        ),
        pytest.param(
            {
                "allOf": [{"type": "string"}, {"minLength": 3}],
                "default": "sample string",
            },
            AllOf(String(), Element(minLength=3), default="sample string"),
            id="allOf-with-multiple-sub-elements-and-default",
        ),
        pytest.param(
            {"type": "string", "allOf": [{"minLength": 3}]},
            AllOf(String(), Element(minLength=3)),
            id="allOf-with-one-sub-element-and-outer-type",
        ),
        pytest.param(
            {"type": "string", "allOf": [{"minLength": 3}, {"maxLength": 5}]},
            AllOf(String(), Element(minLength=3), Element(maxLength=5)),
            id="allOf-with-multiple-sub-elements-and-outer-type",
        ),
        pytest.param(
            {
                "oneOf": [{"minimum": 3}, {"maximum": 5}],
                "anyOf": [{"type": "number"}, {"type": "integer"}],
                "allOf": [{"minimum": 0}, {"maximum": 10}],
                "not": {"multipleOf": 2},
            },
            AllOf(
                Element(minimum=0),
                Element(maximum=10),
                OneOf(Element(minimum=3), Element(maximum=5)),
                AnyOf(Number(), Integer()),
                Not(Element(multipleOf=2)),
            ),
            id="all-compositions-no-outer",
        ),
        pytest.param(
            {
                "maximum": 7,
                "oneOf": [{"minimum": 3}, {"maximum": 5}],
                "anyOf": [{"type": "number"}, {"type": "integer"}],
                "allOf": [{"minimum": 0}, {"maximum": 10}],
                "not": {"multipleOf": 2},
            },
            AllOf(
                Element(maximum=7),
                Element(minimum=0),
                Element(maximum=10),
                OneOf(Element(minimum=3), Element(maximum=5)),
                AnyOf(Number(), Integer()),
                Not(Element(multipleOf=2)),
            ),
            id="all-compositions-with-outer",
        ),
    ],
)
def test_parse_composition_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected


def test_parse_single_list_typed_schema_returns_one_type():
    parsed = parse_element({"type": ["string"]})
    assert parsed == String()


class TestPrimitiveCompositionWithOuterKeywords:
    @staticmethod
    @pytest.fixture(scope="class")
    def element():
        schema = {
            "type": "integer",
            "oneOf": [
                {"minimum": 1, "maximum": 3},
                {"minimum": 2, "maximum": 4},
            ],
        }
        return parse_element(schema)

    @staticmethod
    def test_element_is_parsed_correctly(element):
        assert element == AllOf(
            Integer(),
            OneOf(Element(minimum=1, maximum=3), Element(minimum=2, maximum=4)),
        )

    @staticmethod
    def test_element_validates_type(element):
        with pytest.raises(ValidationError):
            _ = element(3.5)

    @staticmethod
    @pytest.mark.parametrize("value", [2, 3])
    def test_element_fails_on_bad_value(element, value):
        with pytest.raises(ValidationError):
            _ = element(value)

    @staticmethod
    @pytest.mark.parametrize("value", [1, 4])
    def test_element_accepts_correct_value(element, value):
        with no_raise():
            _ = element(value)


def test_parse_allOf_with_outer_default_does_not_override_other_element():
    sub_schema = {"type": "object", "title": "Child"}
    schema = {"type": "object", "title": "Parent", "properties": {}}
    schema["properties"]["value"] = sub_schema
    schema["properties"]["other"] = {
        "allOf": [sub_schema],
        "default": {"foo": "bar"},
    }

    class Child(Object):
        pass

    class Parent(Object):
        value = Property(Child)
        other = Property(AllOf(Child, default={"foo": "bar"}))

    assert parse_element(schema) == Parent


def test_parse_anyOf_with_one_empty_element():
    schema = {"anyOf": [{"type": "number"}, {}]}
    element = parse_element(schema)
    with no_raise():
        _ = element("foo")
