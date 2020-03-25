from statham.dsl.constants import Maybe
from statham.dsl.elements import Object, String
from statham.dsl.parser import parse
from statham.dsl.property import Property
from statham.serializer import serialize_python, _serialize_object


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
    assert (
        serialize_python(*parse(SCHEMA))
        == """from typing import List, Union

from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Integer,
    Null,
    Number,
    OneOf,
    Object,
    String,
)
from statham.dsl.property import Property


class Category(Object):

    default = {'value': 'none'}

    value: Maybe[str] = Property(String())


class Parent(Object):

    category: Category = Property(Category, required=True)

    _default: Maybe[str] = Property(String(), name='default')


class Other(Object):

    value: Maybe[int] = Property(Integer())
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
        _serialize_object(StringWrapper)
        == """class StringWrapper(Object):

    value: str = Property(String(), required=True)
"""
    )


def test_serialize_object_wrapper_object():
    assert (
        _serialize_object(ObjectWrapper)
        == """class ObjectWrapper(Object):

    value: Maybe[StringWrapper] = Property(StringWrapper)
"""
    )
