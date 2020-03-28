from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Object, ObjectOptions, String
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.parser import name_counter, parse_element
from statham.dsl.property import Property


class EmptyModel(Object):
    pass


class OptionalStringWrapper(Object):
    value = Property(String())


class StringWrapper(Object):
    value = Property(String(), required=True)


class ObjectWrapper(Object):
    value = Property(StringWrapper, required=True)


class ObjectWithDefaultProp(Object):
    default = {"default": "a string"}

    _default = Property(String(), source="default")


class ObjectWithAdditionalPropElement(Object):
    options = ObjectOptions(additionalProperties=String())


class ObjectWithAdditionalPropTrue(Object):
    options = ObjectOptions(additionalProperties=True)


class ObjectWithAdditionalPropFalse(Object):
    options = ObjectOptions(additionalProperties=False)


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
                "title": "ObjectWrapper",
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
        pytest.param(
            {
                "type": "object",
                "title": "ObjectWithDefaultProp",
                "default": {"default": "a string"},
                "properties": {"default": {"type": "string"}},
            },
            ObjectWithDefaultProp,
            id="with-property-named-default",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "ObjectWithAdditionalPropElement",
                "additionalProperties": {"type": "string"},
            },
            ObjectWithAdditionalPropElement,
            id="with-additional-properties-schema",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "ObjectWithAdditionalPropTrue",
                "additionalProperties": True,
            },
            ObjectWithAdditionalPropTrue,
            id="with-additional-properties-true",
        ),
        pytest.param(
            {
                "type": "object",
                "title": "ObjectWithAdditionalPropFalse",
                "additionalProperties": False,
            },
            ObjectWithAdditionalPropFalse,
            id="with-additional-properties-false",
        ),
    ],
)
def test_parse_object_produces_expected_element(
    schema: Dict[str, Any], expected: Element
):
    assert parse_element(schema) == expected


def test_parse_object_with_no_title_raises():
    with pytest.raises(SchemaParseError):
        parse_element({"type": "object"})


def test_parse_object_with_same_name_are_enumerated():
    schema = {
        "type": "object",
        "title": "Name",
        "additionalProperties": {"type": "object", "title": "Name"},
    }
    element = parse_element(schema)
    assert isinstance(element, ObjectMeta)
    assert element.__name__ == "Name_1"
    assert isinstance(element.options.additionalProperties, ObjectMeta)
    assert element.options.additionalProperties.__name__ == "Name"


def test_name_counter():
    counter = name_counter()
    assert bool(counter)

    def next_name(name):
        return next(counter[name])

    names = ["first_name", "first_name", "second_name", "first_name"]
    name_counts = list(map(next_name, names))
    assert name_counts == [0, 1, 0, 2]
