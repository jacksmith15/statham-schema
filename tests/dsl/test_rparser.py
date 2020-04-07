import pytest

from statham.dsl.elements import *
from statham.dsl.property import *
from statham.dsl.rparser import parse_element


@pytest.mark.parametrize(
    "schema,expected",
    [
        ({}, Element()),
        ({"type": "string"}, String()),
        ({"type": "integer"}, Integer()),
        ({"type": "null"}, Null()),
        ({"minLength": 3}, Element(minLength=3)),
        ({"type": "string", "minLength": 3}, String(minLength=3)),
        ({"type": "array"}, Array(Element())),
        ({"type": "array", "items": {"type": "string"}}, Array(String())),
    ],
)
def test_simple_schemas(schema, expected):
    assert parse_element(schema) == expected


def test_recursive_items_single_degree():
    schema = {}
    schema["items"] = schema
    element = parse_element(schema)
    assert element.items is element


def test_recursive_items_second_degree():
    schema = {"items": {}}
    schema["items"]["items"] = schema
    element = parse_element(schema)
    assert element.items.items is element
    assert element.items.items.items is element.items
    assert element.items is not element


def test_recursive_properties():
    schema = {"properties": {}}
    schema["properties"]["foo"] = schema
    element = parse_element(schema)
    assert element.properties["foo"].element is element


def test_object_parser():
    class Foo(Object):
        value = Property(String())

    schema = {
        "type": "object",
        "title": "Foo",
        "properties": {"value": {"type": "string"}},
    }
    element = parse_element(schema)
    assert element == Foo


def test_object_recursive_properties():
    schema = {"type": "object", "title": "Recursive", "properties": {}}
    schema["properties"]["value"] = schema
    element = parse_element(schema)
    assert element.properties["value"].element is element
