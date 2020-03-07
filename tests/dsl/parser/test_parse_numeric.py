from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Integer, Number
from statham.dsl.parser import parse


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param(
            {"type": "integer"}, Integer(), id="integer-with-no-keywords"
        ),
        pytest.param(
            {
                "type": "integer",
                "default": 4,
                "minimum": 2,
                "exclusiveMinimum": 2,
                "maximum": 7,
                "exclusiveMaximum": 7,
                "multipleOf": 2,
            },
            Integer(
                default=4,
                minimum=2,
                exclusiveMinimum=2,
                maximum=7,
                exclusiveMaximum=7,
                multipleOf=2,
            ),
            id="integer-with-all-keywords",
        ),
        pytest.param(
            {"type": "number"}, Number(), id="number-with-no-keywords"
        ),
        pytest.param(
            {
                "type": "number",
                "default": 4.0,
                "minimum": 2.5,
                "exclusiveMinimum": 2.5,
                "maximum": 7.5,
                "exclusiveMaximum": 7.5,
                "multipleOf": 0.5,
            },
            Number(
                default=4.0,
                minimum=2.5,
                exclusiveMinimum=2.5,
                maximum=7.5,
                exclusiveMaximum=7.5,
                multipleOf=0.5,
            ),
            id="number-with-all-keywords",
        ),
    ],
)
def test_parse_boolean_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse(schema) == expected
