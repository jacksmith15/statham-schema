import pytest

from statham.dsl.elements import Element, Integer, Nothing, String
from statham.dsl.elements.properties import Properties
from statham.dsl.property import _Property as Property


def test_properties_default():
    parent = Element()
    properties = Properties(parent, {"value": Property(String())})
    assert "value" in properties
    assert properties["value"].element == String()
    assert properties["value"].parent == parent
    assert "other" in properties
    assert properties["other"].element == Element()
    assert properties["other"].parent == parent
    assert properties.additional == Element()


def test_properties_source():
    parent = Element()
    properties = Properties(parent, {"value": Property(String(), source="val")})
    assert properties["val"].element == String()
    assert properties["val"].parent == parent
    assert properties["value"].element == Element()
    assert properties["value"].parent == parent
    assert properties.additional == Element()


def test_properties_no_additional():
    parent = Element()
    properties = Properties(
        parent, {"value": Property(String())}, additional=False
    )
    assert "value" in properties
    assert properties["value"].element == String()
    assert properties["value"].parent == parent
    assert "other" not in properties
    assert properties["other"].element == Nothing()
    assert properties.additional == Nothing()


def test_properties_specific_additional():
    parent = Element()
    properties = Properties(
        parent, {"value": Property(String())}, additional=Integer()
    )
    assert "value" in properties
    assert properties["value"].element == String()
    assert properties["value"].parent == parent
    assert "other" in properties
    assert properties["other"].element == Integer()
    assert properties["other"].parent == parent
    assert properties.additional == Integer()


def test_properties_pattern():
    parent = Element()
    properties = Properties(
        parent,
        {"value": Property(String())},
        {"^foo": Integer()},
        additional=False,
    )
    assert "value" in properties
    assert "foobar" in properties
    assert "barfoo" not in properties
    assert properties["value"].element == String()
    assert properties["foobar"].element == Integer()
    assert properties["foobar"].parent == parent
    assert properties["foobar"].name == "foobar"


@pytest.mark.parametrize(
    "additional,expected",
    [
        (True, ""),
        (Element(), ""),
        (False, ", additionalProperties=False"),
        (Nothing(), ", additionalProperties=False"),
        (Integer(), ", additionalProperties=Integer()"),
    ],
)
def test_properties_additional_repr(additional, expected):
    parent = Element()
    properties = Properties(
        parent, {"value": Property(String())}, additional=additional
    )
    assert repr(properties) == (
        "Properties({'value': Property(String())}" + f"{expected})"
    )


@pytest.mark.parametrize(
    "pattern,expected",
    [
        ({}, ""),
        ({"^foo": Integer()}, ", patternProperties={'^foo': Integer()}"),
    ],
)
def test_properties_pattern_repr(pattern, expected):
    parent = Element()
    properties = Properties(
        parent, {"value": Property(String())}, pattern=pattern
    )
    assert repr(properties) == (
        "Properties({'value': Property(String())}" + f"{expected})"
    )


def test_properties_iter():
    parent = Element()
    properties = Properties(
        parent,
        {"value": Property(String()), "other": Property(Integer())},
        False,
    )
    assert set(properties) == {"value", "other"}
