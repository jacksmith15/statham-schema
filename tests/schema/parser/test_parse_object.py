from typing import Any, Dict

import pytest

from statham.schema.elements import Element, Nothing, Object, String
from statham.schema.elements.meta import ObjectClassDict, ObjectMeta
from statham.schema.exceptions import SchemaParseError
from statham.schema.parser import _ParseState, parse_element
from statham.schema.property import Property


class EmptyModel(Object):
    pass


class ObjectWithOptionalProperty(Object):
    value = Property(String())


class ObjectWithRequiredProperty(Object):
    value = Property(String(), required=True)


class ObjectWithObjectProperty(Object):
    value = Property(ObjectWithRequiredProperty, required=True)


class ObjectWithDefaultProp(Object, default={"default": "a string"}):

    value = Property(String())


class ObjectWithAdditionalPropElement(Object, additionalProperties=String()):
    pass


class ObjectWithAdditionalPropTrue(Object, additionalProperties=True):
    pass


class ObjectWithAdditionalPropFalse(Object, additionalProperties=False):
    pass


class ObjectWithPatternProps(
    Object, patternProperties={"^foo": Element(), "^(?!foo)": Nothing()}
):
    pass


class ObjectWithSizeValidation(Object, minProperties=1, maxProperties=2):
    pass


class ObjectWithPropertyNames(Object, propertyNames=String(maxLength=3)):
    pass


class ObjectWithConst(Object, const={"foo": "bar"}):
    pass


class ObjectWithEnum(Object, enum=[{"foo": "bar"}, {"qux": "mux"}]):
    pass


class ObjectWithDependencies(
    Object, dependencies={"foo": ["bar"], "qux": Element(minProperties=2)}
):
    pass


PARAMS = [
    pytest.param(
        {"type": "object", "title": "EmptyModel"},
        EmptyModel,
        id="with-no-keywords",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithOptionalProperty",
            "properties": {"value": {"type": "string"}},
        },
        ObjectWithOptionalProperty,
        id="with-not-required-property",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithRequiredProperty",
            "required": ["value"],
            "properties": {"value": {"type": "string"}},
        },
        ObjectWithRequiredProperty,
        id="with-required-property",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithObjectProperty",
            "required": ["value"],
            "properties": {
                "value": {
                    "type": "object",
                    "title": "ObjectWithRequiredProperty",
                    "required": ["value"],
                    "properties": {"value": {"type": "string"}},
                }
            },
        },
        ObjectWithObjectProperty,
        id="with-object-property",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithDefaultProp",
            "default": {"default": "a string"},
            "properties": {"value": {"type": "string"}},
        },
        ObjectWithDefaultProp,
        id="with-default-default",
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
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithPatternProps",
            "patternProperties": {"^foo": True, "^(?!foo)": False},
        },
        ObjectWithPatternProps,
        id="with-pattern-props",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithSizeValidation",
            "minProperties": 1,
            "maxProperties": 2,
        },
        ObjectWithSizeValidation,
        id="with-size-validation",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithPropertyNames",
            "propertyNames": {"type": "string", "maxLength": 3},
        },
        ObjectWithPropertyNames,
        id="with-property-names",
    ),
    pytest.param(
        {"type": "object", "title": "ObjectWithConst", "const": {"foo": "bar"}},
        ObjectWithConst,
        id="with-const",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithEnum",
            "enum": [{"foo": "bar"}, {"qux": "mux"}],
        },
        ObjectWithEnum,
        id="with-enum",
    ),
    pytest.param(
        {
            "type": "object",
            "title": "ObjectWithDependencies",
            "dependencies": {"foo": ["bar"], "qux": {"minProperties": 2}},
        },
        ObjectWithDependencies,
        id="with-dependencies",
    ),
]


@pytest.mark.parametrize("schema,expected", PARAMS)
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
    assert isinstance(element.additionalProperties, ObjectMeta)
    assert element.additionalProperties.__name__ == "Name"


class TestParseState:
    @staticmethod
    @pytest.fixture()
    def base_type():
        return ObjectMeta(
            "Foo", (Object,), ObjectClassDict(), default={"foo": "bar"}
        )

    @staticmethod
    @pytest.fixture()
    def state(base_type):
        state = _ParseState()
        assert state.dedupe(base_type) is base_type
        return state

    @staticmethod
    def test_that_duplicate_type_is_replaced(state, base_type):
        duplicate = ObjectMeta(
            "Foo", (Object,), ObjectClassDict(), default={"foo": "bar"}
        )
        deduped = state.dedupe(duplicate)
        assert deduped is base_type
        assert len(state.seen["Foo"]) == 1
        assert state.seen["Foo"][0] is base_type

    @staticmethod
    def test_that_distinct_type_is_not_replaced(state, base_type):
        distinct = ObjectMeta(
            "Foo", (Object,), ObjectClassDict(), default={"bar": "baz"}
        )
        deduped = state.dedupe(distinct)
        assert deduped is distinct
        assert distinct.__name__ == "Foo_1"
        assert len(state.seen["Foo"]) == 2
        assert state.seen["Foo"][0] is base_type
        assert state.seen["Foo"][1] is distinct


def test_parse_object_with_required_not_properties():
    schema = {"type": "object", "title": "NoProperties", "required": ["value"]}

    class NoProperties(Object):
        value = Property(Element(), required=True)

    assert parse_element(schema) == NoProperties


def test_parse_object_with_invalid_names():
    schema = {
        "type": "object",
        "title": "BadNames",
        "properties": {
            "$ref": {},
            "a sentence": {},
            "multiple\nlines": {},
            "10": {},
        },
    }

    class BadNames(Object):
        dollar_sign_ref = Property(Element(), source="$ref")
        a_sentence = Property(Element(), source="a sentence")
        multiple_lines = Property(Element(), source="multiple\nlines")
        _10 = Property(Element(), source="10")

    assert parse_element(schema) == BadNames
