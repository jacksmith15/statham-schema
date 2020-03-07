import pytest

from statham.dsl.elements import AnyOf, Array, OneOf, String
from statham.dsl.parser import parse


class TestParseAnyOf:
    @staticmethod
    def test_with_empty_list():
        schema = {"anyOf": []}
        with pytest.raises(TypeError):
            _ = parse(schema)

    @staticmethod
    def test_with_single_item():
        schema = {"anyOf": [{"type": "string"}]}
        element = parse(schema)
        assert isinstance(element, AnyOf)
        assert len(element.elements) == 1
        assert isinstance(element.elements[0], String)
        assert repr(element) == ("AnyOf(String())")

    @staticmethod
    def test_with_multi_item():
        schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
            ]
        }
        element = parse(schema)
        assert isinstance(element, AnyOf)
        assert len(element.elements) == 2
        assert isinstance(element.elements[0], String)
        assert isinstance(element.elements[1], Array)
        assert repr(element) == "AnyOf(String(), Array(String()))"

    @staticmethod
    def test_with_multi_type_value():
        schema = {
            "type": ["string", "array"],
            "minLength": 3,
            "minItems": 3,
            "items": {"type": "string", "maxLength": 1},
        }
        element = parse(schema)
        assert isinstance(element, AnyOf)
        assert len(element.elements) == 2
        assert isinstance(element.elements[0], String)
        assert isinstance(element.elements[1], Array)
        assert repr(element) == (
            "AnyOf(String(minLength=3), Array(String(maxLength=1), minItems=3))"
        )


class TestParseOneOf:
    @staticmethod
    def test_with_empty_list():
        schema = {"oneOf": []}
        with pytest.raises(TypeError):
            _ = parse(schema)

    @staticmethod
    def test_with_single_item():
        schema = {"oneOf": [{"type": "string"}]}
        element = parse(schema)
        assert isinstance(element, OneOf)
        assert len(element.elements) == 1
        assert isinstance(element.elements[0], String)
        assert repr(element) == "OneOf(String())"

    @staticmethod
    def test_with_multi_item():
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
            ]
        }
        element = parse(schema)
        assert isinstance(element, OneOf)
        assert len(element.elements) == 2
        assert isinstance(element.elements[0], String)
        assert isinstance(element.elements[1], Array)
        assert repr(element) == "OneOf(String(), Array(String()))"
