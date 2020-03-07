from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, String
from statham.dsl.parser import parse


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
    assert parse(schema) == expected
