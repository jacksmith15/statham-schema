from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Boolean
from statham.dsl.parser import parse_element


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param({"type": "boolean"}, Boolean(), id="no-keywords"),
        pytest.param(
            {"type": "boolean", "default": True},
            Boolean(default=True),
            id="with-default",
        ),
    ],
)
def test_parse_boolean_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected
