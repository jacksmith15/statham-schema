from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Null
from statham.dsl.parser import parse


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
    assert parse(schema) == expected
