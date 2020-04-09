from typing import Any, Dict

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Element, String, Array, Object
from statham.dsl.exceptions import ValidationError
from statham.dsl.property import Property
from tests.helpers import no_raise


@pytest.mark.parametrize(
    "valid,data",
    [
        (True, NotPassed()),
        (True, []),
        (True, [[]]),
        (True, [[], []]),
        (True, [[], [[], []]]),
        (False, 1),
        (False, [1, 2, 3]),
        (False, [[], 1]),
    ],
)
def test_recursive_array_of_arrays_validates_correctly(valid: bool, data: Any):
    element: Array = Array(Element())
    element.items = element
    with no_raise() if valid else pytest.raises((TypeError, ValidationError)):
        _ = element(data)


@pytest.mark.parametrize(
    "valid,data",
    [
        (True, NotPassed()),
        (True, {}),
        (True, {"value": "foo"}),
        (True, {"other": {}}),
        (True, {"value": "foo", "other": {"value": "foo"}}),
        (
            True,
            {
                "value": "foo",
                "other": {"value": "foo", "other": {"value": "foo"}},
            },
        ),
        (False, 1),
        (False, [1, 2, 3]),
        (False, {"other": 1}),
    ],
)
def test_recursive_object_validates_correctly(valid: bool, data: Any):
    class Foo(Object):
        value = Property(String())
        other: Dict[str, Any] = Property(Element())

    Foo.properties["other"].element = Foo

    with no_raise() if valid else pytest.raises((TypeError, ValidationError)):
        _ = Foo(data)


def test_recursive_object_with_default_instance():
    class Foo(Object):
        value = Property(Element())

    Foo.properties["value"].element = Foo
    Foo.default = Foo({})
    Foo()
    Foo({})


def test_recursive_object_with_default_dict():
    class Foo(Object, default={}):
        value = Property(Element())

    Foo.properties["value"].element = Foo
    Foo.default = Foo({})
    Foo()
    Foo({})
