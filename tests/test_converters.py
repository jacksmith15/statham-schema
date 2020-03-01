from attr import attrs, attrib

import pytest

from statham import validators as val
from statham.converters import (
    _safe_instantiate,
    AnyOf,
    Array,
    instantiate,
    OneOf,
    Sentinel,
    TypeItem,
)
from tests.helpers import no_raise


@attrs
class StringWrapper:
    attr = attrib(validator=val.instance_of(str))


@attrs
class IntegerWrapper:
    attr = attrib(validator=val.instance_of(int))


@pytest.mark.parametrize(
    "input_", [{"attr": "foo"}, StringWrapper(attr="foo"), val.NotPassed()]
)
def test_instantiate_is_successful_for_simple_declarations(input_):
    with no_raise():
        _ = instantiate(StringWrapper)(input_)


def test_array_instantiate_is_successful():
    factory = instantiate(Array(StringWrapper))
    with no_raise():
        _ = factory(
            [{"attr": "foo"}, StringWrapper(attr="foo"), val.NotPassed()]
        )


@pytest.mark.parametrize("sentinel", [AnyOf, OneOf])
@pytest.mark.parametrize(
    "input_",
    [
        {"attr": "foo"},
        StringWrapper(attr="foo"),
        {"attr": 1},
        IntegerWrapper(attr=1),
        val.NotPassed(),
    ],
)
def test_composition_instantiate_is_successful(sentinel, input_):
    factory = instantiate(sentinel(StringWrapper, IntegerWrapper))
    with no_raise():
        _ = factory(input_)


@pytest.mark.parametrize("sentinel", [AnyOf, OneOf])
def test_nesting_composition_within_array(sentinel):
    factory = instantiate(Array(sentinel(StringWrapper, IntegerWrapper)))
    with no_raise():
        _ = factory(
            [
                {"attr": "foo"},
                StringWrapper(attr="foo"),
                {"attr": 1},
                IntegerWrapper(attr=1),
                val.NotPassed(),
            ]
        )


@pytest.mark.parametrize(
    "input_",
    [
        {"attr": "foo"},
        StringWrapper(attr="foo"),
        [{"attr": "foo"}, StringWrapper(attr="foo")],
    ],
)
def test_nesting_array_within_a_composition(input_):
    factory = instantiate(AnyOf(StringWrapper, Array(StringWrapper)))
    with no_raise():
        _ = factory(input_)
