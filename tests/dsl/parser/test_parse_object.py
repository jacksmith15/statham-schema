from statham.dsl.elements import String
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.parser import parse
from statham.dsl.property import _Property


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
