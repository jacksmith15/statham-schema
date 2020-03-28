from typing import Any

import pytest

from statham.dsl.constants import Maybe
from statham.dsl.elements import Element, Object, ObjectOptions, String
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


def test_parse_and_serialize_schema_with_additional_options_element():
    schema = {
        "type": "object",
        "title": "StringContainer",
        "additionalProperties": {"type": "string"},
    }
    assert serialize_python(*parse(schema)) == _IMPORT_STATEMENTS + (
        """class StringContainer(Object):

    options = ObjectOptions(additionalProperties=String())
"""
    )


def test_parse_and_serialize_schema_with_option_dependencies():
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


class StringWrapperContainer(Object):

    options = ObjectOptions(additionalProperties=StringWrapper)
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
def test_serialize_object_with_additional_options(additional_properties):
    class AdditionalPropObject(Object):
        options = ObjectOptions(additionalProperties=additional_properties)

    assert AdditionalPropObject.python() == (
        f"""class AdditionalPropObject(Object):

    options = ObjectOptions(additionalProperties={additional_properties})
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
