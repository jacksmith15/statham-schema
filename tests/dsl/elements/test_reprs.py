import pytest

from statham.dsl.elements import (
    AnyOf,
    Array,
    Boolean,
    Element,
    Integer,
    Null,
    Number,
    Object,
    OneOf,
    String,
)
from statham.dsl.property import Property


class RenamedProperty(Object):
    renamed = Property(String(), source="default")
    not_renamed = Property(String(), source="not_renamed")


class StringWrapper(Object):
    value = Property(String(), required=True)


class ObjectWrapper(Object):
    value = Property(StringWrapper)


@pytest.mark.parametrize(
    "element,expected",
    [
        (AnyOf(String()), "AnyOf(String())"),
        (AnyOf(String(), Array(String())), "AnyOf(String(), Array(String()))"),
        (
            AnyOf(String(), Array(String()), default=[]),
            "AnyOf(String(), Array(String()), default=[])",
        ),
        (Array(String()), "Array(String())"),
        (Array(String(), minItems=3), "Array(String(), minItems=3)"),
        (Array([String(), Integer()]), "Array([String(), Integer()])"),
        (
            Array(String(), uniqueItems=True),
            "Array(String(), uniqueItems=True)",
        ),
        (Array(String(), uniqueItems=False), "Array(String())"),
        (Boolean(), "Boolean()"),
        (Boolean(default=True), "Boolean(default=True)"),
        (Integer(), "Integer()"),
        (Integer(minimum=3), "Integer(minimum=3)"),
        (Null(), "Null()"),
        (Null(default=None), "Null(default=None)"),
        (Number(), "Number()"),
        (Number(minimum=3.2), "Number(minimum=3.2)"),
        (OneOf(String()), "OneOf(String())"),
        (OneOf(String(), Array(String())), "OneOf(String(), Array(String()))"),
        (
            OneOf(String(), Array(String()), default=[]),
            "OneOf(String(), Array(String()), default=[])",
        ),
        (String(), "String()"),
        (String(pattern=".*"), "String(pattern='.*')"),
        (Element(), "Element()"),
        (Element(default="foo"), "Element(default='foo')"),
        (Element(minimum=1), "Element(minimum=1)"),
        (Element(additionalProperties=True), "Element()"),
        (
            Element(additionalProperties=False),
            "Element(additionalProperties=False)",
        ),
        (Element(uniqueItems=True), "Element(uniqueItems=True)"),
        (Element(uniqueItems=False), "Element()"),
        (
            Element(propertyNames=String(maxLength=3)),
            "Element(propertyNames=String(maxLength=3))",
        ),
        (ObjectWrapper, "ObjectWrapper"),
        (StringWrapper, "StringWrapper"),
        (
            RenamedProperty.properties["renamed"],
            "Property(String(), source='default')",
        ),
        (RenamedProperty.properties["not_renamed"], "Property(String())"),
    ],
)
def test_reprs_are_correct(element: Element, expected: str):
    assert repr(element) == expected
