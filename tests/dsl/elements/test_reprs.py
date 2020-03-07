import pytest

from statham.dsl.elements import AnyOf, Array, Element, OneOf, String, Object
from statham.dsl.property import Property


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
        (OneOf(String()), "OneOf(String())"),
        (OneOf(String(), Array(String())), "OneOf(String(), Array(String()))"),
        (
            OneOf(String(), Array(String()), default=[]),
            "OneOf(String(), Array(String()), default=[])",
        ),
        (String(), "String()"),
        (String(pattern=".*"), "String(pattern='.*')"),
        (ObjectWrapper, "ObjectWrapper"),
        (StringWrapper, "StringWrapper"),
    ],
)
def test_reprs_are_correct(element: Element, expected: str):
    assert repr(element) == expected


def test_code_property_of_string_wrapper_object():
    assert (
        StringWrapper.code
        == """class StringWrapper(Object):

    value: str = Property(String(), required=True)
"""
    )


def test_code_property_of_object_wrapper_object():
    assert (
        ObjectWrapper.code
        == """class ObjectWrapper(Object):

    value: Maybe[StringWrapper] = Property(StringWrapper)
"""
    )
