from typing import Any, Dict

import pytest

from statham.schema.elements import Element, String
from statham.schema.parser import parse_element


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param({"type": "string"}, String(), id="with-no-keywords"),
        pytest.param(
            {
                "type": "string",
                "default": "sample",
                "format": "my_format",
                "pattern": ".*",
                "minLength": 1,
                "maxLength": 3,
            },
            String(
                default="sample",
                format="my_format",
                pattern=".*",
                minLength=1,
                maxLength=3,
            ),
            id="with-all-keywords",
        ),
    ],
)
def test_parse_string_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected
