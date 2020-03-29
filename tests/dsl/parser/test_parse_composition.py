from typing import Any, Dict

import pytest

from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    Element,
    Integer,
    Number,
    OneOf,
    String,
)
from statham.dsl.exceptions import FeatureNotImplementedError, ValidationError
from statham.dsl.parser import parse_composition, parse_element
from tests.helpers import no_raise


@pytest.mark.parametrize("keyword", ["anyOf", "oneOf"])
def test_parse_composition_fails_with_empty_list(keyword):
    schema = {keyword: []}
    with pytest.raises(TypeError):
        _ = parse_element(schema)


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param(
            {"anyOf": [{"type": "string"}]},
            String(),
            id="anyOf-with-one-sub-element",
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
            {"allOf": [{"type": "string"}, {"minLength": 3}]},
            AllOf(String(), Element(minLength=3)),
            id="allOf-with-multiple-sub-elements",
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
            },
            AllOf(
                Element(minimum=0),
                Element(maximum=10),
                AnyOf(Number(), Integer()),
                OneOf(Element(minimum=3), Element(maximum=5)),
            ),
            id="all-compositions-no-outer",
        ),
        pytest.param(
            {
                "maximum": 7,
                "oneOf": [{"minimum": 3}, {"maximum": 5}],
                "anyOf": [{"type": "number"}, {"type": "integer"}],
                "allOf": [{"minimum": 0}, {"maximum": 10}],
            },
            AllOf(
                Element(maximum=7),
                Element(minimum=0),
                Element(maximum=10),
                AnyOf(Number(), Integer()),
                OneOf(Element(minimum=3), Element(maximum=5)),
            ),
            id="all-compositions-with-outer",
        ),
    ],
)
def test_parse_composition_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected


def test_parse_composition_fails_on_multiple_keyword_args():
    schema = {
        "oneOf": [{"type": "string"}, {"type": "integer"}],
        "anyOf": [
            {"type": "integer", "minimum": 1, "maximum": 2},
            {"type": "integer", "minimum": 5},
            {"type": "string"},
        ],
    }
    with pytest.raises(FeatureNotImplementedError):
        parse_element(schema)


def test_parse_composition_fails_with_no_composition_keywords():
    schema = {}
    with pytest.raises(ValueError):
        parse_composition(schema)


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
