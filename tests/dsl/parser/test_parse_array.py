from typing import Any, Dict

import pytest

from statham.dsl.elements import Array, Element, String
from statham.dsl.parser import parse


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param({"type": "array"}, Array(Element()), id="without-items"),
        pytest.param(
            {"type": "array", "items": {"type": "string"}},
            Array(String()),
            id="with-items",
        ),
        pytest.param(
            {
                "type": "array",
                "items": {"type": "string"},
                "default": ["foo", "bar"],
                "minItems": 1,
                "maxItems": 3,
            },
            Array(String(), default=["foo", "bar"], minItems=1, maxItems=3),
            id="with-items-and-keywords",
        ),
    ],
)
def test_parse_array_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse(schema) == expected
