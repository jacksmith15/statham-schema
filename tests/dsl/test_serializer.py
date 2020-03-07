from statham.dsl.parser import parse
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
        == """from statham.dsl.constants import Maybe
from statham.dsl.elements import (
    AnyOf,
    Array,
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
