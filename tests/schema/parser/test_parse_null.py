from typing import Any, Dict

import pytest

from statham.schema.elements import Element, Null
from statham.schema.parser import parse_element


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param({"type": "null"}, Null(), id="no-keywords"),
        pytest.param(
            {"type": "null", "default": None},
            Null(default=None),
            id="with-default",
        ),
    ],
)
def test_parse_null_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected
