import pytest

from statham.schema.elements import Array, Element, Object, String
from statham.schema.property import Property


class Foo(Object):
    value = Property(String())


class Bar(Object):
    value = Property(String())


class Baz(Object):
    value = Property(String(), required=True)


class Mux(Object):
    value = Property(Array(String()))


class Qux(Object):
    value = Property(String(), source="value_")


class Raz(Object, additionalProperties=False):
    value = Property(String())


class Maz(Object, additionalProperties=False):
    value = Property(String())


class Taz(Object, minProperties=1, maxProperties=2):
    value = Property(String())


class Doo(Object, const={"value": "foo"}):
    value = Property(String())


InlineFoo = Object.inline("InlineFoo", properties={"value": Property(String())})
InlineBar = Object.inline("InlineBar", properties={"value": Property(String())})
InlineBaz = Object.inline(
    "InlineBaz", properties={"value": Property(String(), required=True)}
)


@pytest.mark.parametrize(
    "left,right",
    [
        (String(), String()),
        (String(minLength=3), String(minLength=3)),
        (Array(String()), Array(String())),
        (Array(String(), minItems=3), Array(String(), minItems=3)),
        (Array(String(minLength=3)), Array(String(minLength=3))),
        (
            Array(Element(), contains=String()),
            Array(Element(), contains=String()),
        ),
        (Foo, Bar),
        (Raz, Maz),
        (Foo, InlineFoo),
        (InlineFoo, InlineBar),
        (Baz, InlineBaz),
    ],
)
def test_equivalent_schemas_are_equal(left, right):
    assert left == right


@pytest.mark.parametrize(
    "left,right",
    [
        (String(), String(default="foo")),
        (Array(String()), Array(String(), minItems=3)),
        (Array(String()), Array(String(minLength=3))),
        (Array(Element()), Array(Element(), contains=String())),
        (Foo, Baz),
        (Foo, Mux),
        (Foo, Qux),
        (Foo, Raz),
        (Foo, Taz),
        (Foo, Doo),
        (Foo, InlineBaz),
        (InlineFoo, Baz),
        (InlineFoo, InlineBaz),
    ],
)
def test_non_equivalent_schemas_are_not_equal(left, right):
    assert left != right
