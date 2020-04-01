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
    with pytest.raises(KeyError):
        _ = properties["other"]
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
