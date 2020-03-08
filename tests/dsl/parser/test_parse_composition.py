from typing import Any, Dict

import pytest

from statham.dsl.elements import AnyOf, Array, Element, Integer, OneOf, String
from statham.dsl.parser import parse_element


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
            AnyOf(String()),
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
            OneOf(String()),
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
    ],
)
def test_parse_composition_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected
