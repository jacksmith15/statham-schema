from typing import Any

import pytest

from statham.dsl.constants import Maybe
from statham.dsl.elements import Element, Object, String

# False positive: https://github.com/PyCQA/pylint/issues/3202
from statham.dsl.elements import Nothing  # pylint: disable=unused-import
from statham.dsl.parser import parse
from statham.dsl.property import Property
from statham.serializer import _IMPORT_STATEMENTS, serialize_python


SCHEMA = {
    "type": "object",
    "title": "Parent",
    "required": ["category"],
    "properties": {
        "category": {
            "type": "object",
            "title": "Category",
            "properties": {"value": {"type": "string"}},
            "default": {"value": "none"},
        },
        "default": {"type": "string"},
    },
    "definitions": {
        "other": {
            "type": "object",
            "title": "Other",
            "properties": {"value": {"type": "integer"}},
        }
    },
}


def test_schema_reserializes_to_expected_python_string():
    assert serialize_python(*parse(SCHEMA)) == _IMPORT_STATEMENTS + (
        """class Category(Object):

    default = {'value': 'none'}

    value: Maybe[str] = Property(String())


class Parent(Object):

    category: Category = Property(Category, required=True)

    _default: Maybe[str] = Property(String(), source='default')


class Other(Object):

    value: Maybe[int] = Property(Integer())
"""
    )


def test_parse_and_serialize_schema_with_self_property():
    schema = {
        "type": "object",
        "title": "MyObject",
        "properties": {"self": {"type": "string"}},
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class MyObject(Object):

    self: Maybe[str] = Property(String())
"""
    )


def test_parse_and_serialize_schema_with_no_args():
    schema = {"type": "object", "title": "NoProps"}
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class NoProps(Object):

    pass
"""
    )


def test_parse_and_serialize_schema_with_additional_properties_element():
    schema = {
        "type": "object",
        "title": "StringContainer",
        "additionalProperties": {"type": "string"},
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class StringContainer(Object, additionalProperties=String()):

    pass
"""
    )


def test_parse_and_serialize_schema_with_additional_property_dependencies():
    schema = {
        "type": "object",
        "title": "StringWrapperContainer",
        "additionalProperties": {
            "type": "object",
            "title": "StringWrapper",
            "properties": {"value": {"type": "string"}},
        },
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class StringWrapper(Object):

    value: Maybe[str] = Property(String())


class StringWrapperContainer(Object, additionalProperties=StringWrapper):

    pass
"""
    )


def test_parse_and_serialize_schema_with_untyped_dependency():
    schema = {
        "type": "object",
        "title": "Foo",
        "properties": {
            "value": {
                "additionalProperties": {"type": "object", "title": "Bar"}
            }
        },
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class Bar(Object):

    pass


class Foo(Object):

    value: Maybe[Any] = Property(Element(additionalProperties=Bar))
"""
    )


def test_parse_and_serialize_schema_with_composition_keywords():
    schema = {
        "type": "object",
        "title": "MyObject",
        "properties": {
            "any": {"anyOf": [{"type": "string"}, {"minLength": 3}]},
            "all": {"allOf": [{"type": "string"}, {"minLength": 3}]},
            "one": {"oneOf": [{"type": "string"}, {"minLength": 3}]},
            "not": {"not": {"type": "string"}},
        },
    }
    # pylint: disable=line-too-long
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class MyObject(Object):

    any: Maybe[Any] = Property(AnyOf(String(), Element(minLength=3)))

    all: Maybe[str] = Property(AllOf(String(), Element(minLength=3)))

    one: Maybe[Any] = Property(OneOf(String(), Element(minLength=3)))

    _not: Maybe[Any] = Property(Not(String()), source='not')
"""
    )


def test_parse_and_serialize_schema_with_bad_name():
    schema = {
        "type": "object",
        "title": "BadName",
        "required": ["$id"],
        "properties": {"$id": {"type": "string"}},
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class BadName(Object):

    dollar_sign_id: str = Property(String(), required=True, source='$id')
"""
    )


def test_annotation_for_property_with_default_is_not_maybe():
    prop = Property(String(default="sample"), required=False)
    assert prop.annotation == "str"


class StringWrapper(Object):

    value: str = Property(String(), required=True)


class ObjectWrapper(Object):

    value: Maybe[str] = Property(StringWrapper)


def test_serialize_string_wrapper_object():
    assert (
        StringWrapper.python()
        == """class StringWrapper(Object):

    value: str = Property(String(), required=True)
"""
    )


def test_serialize_object_wrapper_object():
    assert (
        ObjectWrapper.python()
        == """class ObjectWrapper(Object):

    value: Maybe[StringWrapper] = Property(StringWrapper)
"""
    )


@pytest.mark.parametrize("additional_properties", [String(), False])
def test_serialize_object_with_additional_properties(additional_properties):
    class AdditionalPropObject(
        Object, additionalProperties=additional_properties
    ):
        pass

    # pylint: disable=line-too-long
    assert AdditionalPropObject.python() == (
        f"""class AdditionalPropObject(Object, additionalProperties={additional_properties}):

    pass
"""
    )


def test_serialize_object_with_untyped_property():
    class MyObject(Object):

        value: Any = Property(
            Element(
                default="foo",
                minItems=3,
                maxItems=5,
                minimum=3,
                maximum=5,
                minLength=3,
                maxLength=5,
                required=["value"],
                properties={"value": Property(String(), required=True)},
                additionalProperties=String(),
                items=String(),
            )
        )

    assert (
        MyObject.python()
        == """class MyObject(Object):

    value: Any = Property(Element(default='foo', items=String(), minItems=3, maxItems=5, minimum=3, maximum=5, minLength=3, maxLength=5, required=['value'], properties={'value': Property(String(), required=True)}, additionalProperties=String()))
"""
    )


def test_serialize_object_with_pattern_properties():
    class MyObject(
        Object, patternProperties={"^foo": Element(), "^(?!foo)": Nothing()}
    ):
        pass

    # pylint: disable=line-too-long
    assert MyObject.python() == (
        """class MyObject(Object, patternProperties={'^foo': Element(), '^(?!foo)': Nothing()}):

    pass
"""
    )


def test_serialize_object_with_size_validation():
    class MyObject(Object, minProperties=1, maxProperties=2):
        pass

    assert MyObject.python() == (
        """class MyObject(Object, minProperties=1, maxProperties=2):

    pass
"""
    )


def test_serialize_object_with_property_names():
    class MyObject(Object, propertyNames=String(maxLength=3)):
        pass

    assert MyObject.python() == (
        """class MyObject(Object, propertyNames=String(maxLength=3)):

    pass
"""
    )


def test_serialize_object_with_const():
    class MyObject(Object, const={"foo": "bar"}):
        pass

    assert MyObject.python() == (
        """class MyObject(Object, const={'foo': 'bar'}):

    pass
"""
    )


def test_serialize_object_with_enum():
    class MyObject(Object, enum=[{"foo": "bar"}, {"qux": "mux"}]):
        pass

    assert MyObject.python() == (
        """class MyObject(Object, enum=[{'foo': 'bar'}, {'qux': 'mux'}]):

    pass
"""
    )


def test_serialize_object_with_dependencies():
    class MyObject(
        Object, dependencies={"foo": ["bar"], "qux": Element(minProperties=2)}
    ):
        pass

    # pylint: disable=line-too-long
    assert MyObject.python() == (
        """class MyObject(Object, dependencies={'foo': ['bar'], 'qux': Element(minProperties=2)}):

    pass
"""
    )
