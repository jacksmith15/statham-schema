from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Object, String
from statham.dsl.parser import parse
from statham.dsl.property import Property


class EmptyModel(Object):
    pass


class OptionalStringWrapper(Object):
    value = Property(String())


class StringWrapper(Object):
    value = Property(String(), required=True)


class ObjectWrapper(Object):
    value = Property(StringWrapper, required=True)


@pytest.mark.parametrize(
    "schema,expected",
    [
        pytest.param(
            {"type": "object", "title": "EmptyModel"},
            EmptyModel,
            id="with-no-keywords",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "OptionalStringWrapper",
                "properties": {"value": {"type": "string"}},
            },
            OptionalStringWrapper,
            id="with-not-required-property",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "StringWrapper",
                "required": ["value"],
                "properties": {"value": {"type": "string"}},
            },
            StringWrapper,
            id="with-required-property",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "StringWrapperWrapper",
                "required": ["value"],
                "properties": {
                    "value": {
                        "type": "object",
                        "title": "StringWrapper",
                        "required": ["value"],
                        "properties": {"value": {"type": "string"}},
                    }
                },
            },
            ObjectWrapper,
            id="with-object-property",
        ),
    ],
)
def test_parse_object_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse(schema) == expected
