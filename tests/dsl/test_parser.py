import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import AnyOf, Array, Object, OneOf, Element, String
from statham.dsl.elements.meta import ObjectClassDict, ObjectMeta
from statham.dsl.parser import parse
from statham.dsl.property import _Property


def test_parsing_empty_schema_results_in_base_element():
    assert type(parse({})) is Element


def test_parsing_schema_with_unknown_fields_ignores_them():
    assert type(parse({"foo": "bar"})) is Element


class TestParseString:
    @staticmethod
    @pytest.mark.parametrize(
        "schema",
        [{"type": "string"}, {"type": "string", "other_property": "value"}],
    )
    def test_with_no_args(schema):
        element = parse(schema)
        assert isinstance(element, String)
        assert element.default == NotPassed()
        assert element.format == NotPassed()
        assert element.pattern == NotPassed()
        assert element.minLength == NotPassed()
        assert element.maxLength == NotPassed()
        assert repr(element) == "String()"

    @staticmethod
    def test_with_full_args():
        schema = {
            "type": "string",
            "default": "foobar",
            "format": "my_format",
            "pattern": ".*",
            "minLength": 3,
            "maxLength": 5,
        }

        element = parse(schema)
        assert isinstance(element, String)
        assert element.default == "foobar"
        assert element.format == "my_format"
        assert element.pattern == ".*"
        assert element.minLength == 3
        assert element.maxLength == 5
        assert repr(element) == (
            """String(default='foobar', format='my_format', pattern='.*', minLength=3, maxLength=5)"""
        )


class TestParseArray:
    @staticmethod
    def test_with_no_items():
        with pytest.raises(TypeError):
            _ = parse({"type": "array"})

    @staticmethod
    def test_with_just_items():
        schema = {"type": "array", "items": {"type": "string"}}
        element = parse(schema)
        assert isinstance(element, Array)
        assert element.default == NotPassed()
        assert element.minItems == NotPassed()
        assert element.maxItems == NotPassed()
        assert isinstance(element.items, String)
        assert repr(element) == "Array(String())"

    @staticmethod
    def test_with_full_args():
        schema = {
            "type": "array",
            "items": {"type": "string"},
            "default": ["foo", "bar"],
            "minItems": 1,
            "maxItems": 3,
        }
        element = parse(schema)
        assert isinstance(element, Array)
        assert element.default == ["foo", "bar"]
        assert element.minItems == 1
        assert element.maxItems == 3
        assert isinstance(element.items, String)
        assert repr(element) == (
            """Array(String(), default=['foo', 'bar'], minItems=1, maxItems=3)"""
        )


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
        assert repr(element) == ("""AnyOf(String())""")

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
        assert repr(element) == ("""AnyOf(String(), Array(String()))""")


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
        assert repr(element) == ("""OneOf(String())""")

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
        assert repr(element) == ("""OneOf(String(), Array(String()))""")


class TestParseObject:
    @staticmethod
    def test_with_no_args():
        schema = {"type": "object", "title": "EmptyModel"}
        element = parse(schema)
        assert isinstance(element, ObjectMeta)
        assert element.__name__ == "EmptyModel"
        assert element.properties == {}
        assert element.code == (
            """class EmptyModel(Object):

    pass
"""
        )

    @staticmethod
    def test_with_not_required_property():
        schema = {
            "type": "object",
            "title": "StringWrapper",
            "properties": {"value": {"type": "string"}},
        }
        element = parse(schema)
        assert isinstance(element, ObjectMeta)
        assert element.__name__ == "StringWrapper"
        assert len(element.properties) == 1
        assert "value" in element.properties
        property_ = element.properties["value"]
        assert isinstance(property_, _Property)
        assert isinstance(property_.element, String)
        assert not property_.required
        assert element.code == (
            """class StringWrapper(Object):

    value: Maybe[str] = Property(String())
"""
        )

    @staticmethod
    def test_with_required_property():
        schema = {
            "type": "object",
            "title": "StringWrapper",
            "required": ["value"],
            "properties": {"value": {"type": "string"}},
        }
        element = parse(schema)
        assert isinstance(element, ObjectMeta)
        assert element.__name__ == "StringWrapper"
        assert len(element.properties) == 1
        assert "value" in element.properties
        property_ = element.properties["value"]
        assert isinstance(property_, _Property)
        assert isinstance(property_.element, String)
        assert property_.required
        assert element.code == (
            """class StringWrapper(Object):

    value: str = Property(String(), required=True)
"""
        )

    @staticmethod
    def test_with_property_referencing_other_object():
        inner_schema = {
            "type": "object",
            "title": "StringWrapper",
            "required": ["value"],
            "properties": {"value": {"type": "string"}},
        }
        schema = {
            "type": "object",
            "title": "StringWrapperWrapper",
            "required": ["value"],
            "properties": {"value": inner_schema},
        }
        element = parse(schema)
        assert isinstance(element, ObjectMeta)
        assert element.__name__ == "StringWrapperWrapper"
        assert len(element.properties) == 1
        assert "value" in element.properties
        property_ = element.properties["value"]
        assert isinstance(property_, _Property)
        assert property_.required

        inner_element = property_.element
        assert isinstance(inner_element, ObjectMeta)
        assert inner_element.__name__ == "StringWrapper"
        assert len(inner_element.properties) == 1
        assert "value" in inner_element.properties
        inner_property = inner_element.properties["value"]
        assert isinstance(inner_property, _Property)
        assert isinstance(inner_property.element, String)
        assert inner_property.required

        assert element.code == (
            """class StringWrapperWrapper(Object):

    value: StringWrapper = Property(StringWrapper, required=True)
"""
        )
        assert inner_element.code == (
            """class StringWrapper(Object):

    value: str = Property(String(), required=True)
"""
        )
