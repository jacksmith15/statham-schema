import pytest

from statham.schema.elements import Element, Object
from statham.schema.exceptions import FeatureNotImplementedError
from statham.schema.parser import parse, parse_element


def test_parser_detects_definitions():
    schema = {
        "definitions": {
            "foo": {"type": "object", "title": "Foo"},
            "bar": {"type": "object", "title": "Bar"},
        }
    }

    class Foo(Object):
        pass

    class Bar(Object):
        pass

    assert parse(schema) == [Element(), Foo, Bar]


def test_parser_detect_top_level():
    schema = {"type": "object", "title": "Foo"}

    class Foo(Object):
        pass

    assert parse(schema) == [Foo]


def test_parser_detects_top_level_and_definitions():
    schema = {
        "type": "object",
        "title": "Foo",
        "definitions": {
            "bar": {"type": "object", "title": "bar"},
            "baz": {"type": "object", "title": "baz"},
        },
    }

    class Foo(Object):
        pass

    class Bar(Object):
        pass

    class Baz(Object):
        pass

    assert parse(schema) == [Foo, Bar, Baz]


def test_parser_does_not_create_duplicates():
    schema = {
        "type": "object",
        "title": "Foo",
        "definitions": {"bar": {"type": "object", "title": "bar"}},
    }
    schema["definitions"]["baz"] = schema["definitions"]["bar"]
    assert schema["definitions"]["baz"] is schema["definitions"]["bar"]
    parsed = parse(schema)
    assert len(parsed) == 3
    assert parsed[1] is parsed[2]


def test_parser_detects_cyclical_references():
    schema = {"type": "object", "properties": {}}
    schema["properties"]["value"] = schema
    with pytest.raises(FeatureNotImplementedError):
        _ = parse_element(schema)
