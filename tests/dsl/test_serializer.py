from statham.dsl.elements import String
from statham.dsl.parser import parse
from statham.dsl.property import Property
from statham.dsl.serializer import serialize_python


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
        }
    },
}


def test_schema_reserializes_to_expected_python_string():
    assert (
        serialize_python(parse(SCHEMA))
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
"""
    )


def test_annotation_for_property_with_default_is_not_maybe():
    prop = Property(String(default="sample"), required=False)
    assert prop.annotation == "str"
