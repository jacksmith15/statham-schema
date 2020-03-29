from typing import Any, Dict

import pytest

from statham.dsl.elements import Element, Object, ObjectOptions, String
from statham.dsl.elements.meta import ObjectClassDict, ObjectMeta
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.parser import ParseState, parse_element
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


class TestParseState:
    @staticmethod
    @pytest.fixture()
    def base_type():
        return ObjectMeta(
            "Foo", (Object,), ObjectClassDict(default={"foo": "bar"})
        )

    @staticmethod
    @pytest.fixture()
    def state(base_type):
        state = ParseState()
        assert state.dedupe(base_type) is base_type
        return state

    @staticmethod
    def test_that_duplicate_type_is_replaced(state, base_type):
        duplicate = ObjectMeta(
            "Foo", (Object,), ObjectClassDict(default={"foo": "bar"})
        )
        deduped = state.dedupe(duplicate)
        assert deduped is base_type
        assert len(state.seen["Foo"]) == 1
        assert state.seen["Foo"][0] is base_type

    @staticmethod
    def test_that_distinct_type_is_not_replaced(state, base_type):
        distinct = ObjectMeta(
            "Foo", (Object,), ObjectClassDict(default={"bar": "baz"})
        )
        deduped = state.dedupe(distinct)
        assert deduped is distinct
        assert distinct.__name__ == "Foo_1"
        assert len(state.seen["Foo"]) == 2
        assert state.seen["Foo"][0] is base_type
        assert state.seen["Foo"][1] is distinct
