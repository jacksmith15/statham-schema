import pytest

from statham.dsl.elements import String, Object, ObjectOptions, Array
from statham.dsl.property import Property


class Foo(Object):
    value = Property(String())


class Bar(Object):
    value = Property(String())


class Baz(Object):
    value = Property(String(), required=True)


class Mux(Object):
    value = Property(Array(String()))


class Qux(Object):
    value = Property(String(), source="_value")


class Raz(Object):
    options = ObjectOptions(additionalProperties=False)
    value = Property(String())


class Maz(Object):
    options = ObjectOptions(additionalProperties=False)
    value = Property(String())


@pytest.mark.parametrize(
    "left,right",
    [
        (String(), String()),
        (String(minLength=3), String(minLength=3)),
        (Array(String()), Array(String())),
        (Array(String(), minItems=3), Array(String(), minItems=3)),
        (Array(String(minLength=3)), Array(String(minLength=3))),
        (Foo, Bar),
        (Raz, Maz),
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
        (Foo, Baz),
        (Foo, Mux),
        (Foo, Qux),
        (Foo, Raz),
    ],
)
def test_non_equivalent_schemas_are_not_equal(left, right):
    assert left != right
