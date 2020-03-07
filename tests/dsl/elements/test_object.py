from typing import List, Union
import pytest

from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.elements import Array, Object, OneOf, String
from statham.dsl.property import Property
from statham.exceptions import ValidationError
from tests.helpers import no_raise


class StringWrapper(Object):

    value: str = Property(String(minLength=3), required=True)


class ListWrapper(Object):

    list_of_stuff: Maybe[List[Union[StringWrapper, str]]] = Property(
        Array(OneOf(StringWrapper, String(minLength=3)), minItems=1)
    )


class ObjectWrapper(Object):

    obj: StringWrapper = Property(StringWrapper, required=True)


@pytest.mark.parametrize("param", [dict(value="foo")])
def test_string_wrapper_vaccepts_valid_arguments(param):
    with no_raise():
        _ = StringWrapper(param)


@pytest.mark.parametrize("param", [dict(value="fo"), dict(), dict(value=3)])
def test_string_wrapper_fails_on_invalid_arguments(param):
    with pytest.raises(ValidationError):
        _ = StringWrapper(param)


@pytest.mark.parametrize(
    "param",
    [
        dict(),
        dict(list_of_stuff=["foo"]),
        dict(list_of_stuff=[{"value": "foo"}]),
        dict(list_of_stuff=[StringWrapper({"value": "foo"})]),
        dict(
            list_of_stuff=[
                "foo",
                {"value": "foo"},
                StringWrapper({"value": "foo"}),
            ]
        ),
    ],
)
def test_list_wrapper_accepts_valid_arguments(param):
    with no_raise():
        _ = ListWrapper(param)


def test_list_wrapper_assigns_not_assed_correctly():
    instance = ListWrapper({})
    assert instance.list_of_stuff is NotPassed()


@pytest.mark.parametrize(
    "param",
    [
        dict(list_of_stuff=[]),
        dict(list_of_stuff=["fo"]),
        dict(list_of_stuff=[1]),
        dict(list_of_stuff=[{"value": 1}]),
        dict(list_of_stuff=["foo", {"value": 1}]),
        dict(list_of_stuff=[1, {"value": "foo"}]),
        dict(not_a="property"),
    ],
)
def test_list_wrapper_fails_on_invalid_arguments(param):
    with pytest.raises(ValidationError):
        _ = ListWrapper(param)


class TestSchemaWithDefault:
    class DefaultStringWrapper(Object):

        default = dict(value="bar")

        value: str = Property(String(minLength=3), required=True)

    def test_that_it_accepts_no_args(self):
        with no_raise():
            instance = self.DefaultStringWrapper()
        assert instance.value == "bar"

    def test_that_it_accepts_an_arg(self):
        with no_raise():
            instance = self.DefaultStringWrapper({"value": "baz"})
        assert instance.value == "baz"


class TestSchemaPropertyWithDefault:
    class StringDefaultWrapper(Object):

        value: str = Property(String(default="bar"), required=True)

    def test_that_it_accepts_no_args(self):
        with no_raise():
            instance = self.StringDefaultWrapper({})
        assert instance.value == "bar"

    def test_that_it_accepts_an_arg(self):
        with no_raise():
            instance = self.StringDefaultWrapper({"value": "baz"})
        assert instance.value == "baz"


def test_object_annotation():
    assert StringWrapper.annotation == StringWrapper.__name__
