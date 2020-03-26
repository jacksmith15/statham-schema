from typing import Any, List, Union
import pytest

from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.elements import Array, Integer, Object, OneOf, String
from statham.dsl.elements.meta import ObjectOptions
from statham.dsl.property import Property
from statham.dsl.exceptions import SchemaDefinitionError, ValidationError
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


@pytest.mark.parametrize(
    "instance,expected",
    [(StringWrapper({"value": "foo"}), "StringWrapper(value='foo')")],
)
def test_object_instance_reprs(instance, expected):
    assert repr(instance) == expected


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


class TestRenamedProperties:
    class PropertyRename(Object):
        default = {"default": "string"}

        _default = Property(String(), source="default")

    def test_that_it_accepts_no_args(self):
        with no_raise():
            instance = self.PropertyRename()
        assert instance._default == "string"

    def test_that_it_accepts_explicit_args(self):
        with no_raise():
            instance = self.PropertyRename({"default": "another string"})
        assert instance._default == "another string"

    def test_that_it_fails_to_accept_outer_arg_name(self):
        with pytest.raises(ValidationError):
            _ = self.PropertyRename({"_default": "string"})


class TestBadPropertyConflictErrors:
    def test_using_a_bad_property_raises_specific_error(self):
        with pytest.raises(SchemaDefinitionError):

            class MyObject(Object):
                default = Property(String())


class TestAdditionalPropertiesAsElement:
    class MyObject(Object):

        options = ObjectOptions(additionalProperties=Integer())
        value = Property(String())

    def test_valid_instantiation(self):
        with no_raise():
            instance = self.MyObject({"value": "foo", "other_value": 3})
        assert instance.value == "foo"
        assert instance.additional_properties["other_value"] == 3

    def test_additional_value_is_not_accepted_for_declared_value(self):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": 1, "other_value": 3})

    def test_bad_additional_value_is_not_accepted(self):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": "foo", "other_value": "bad"})


class TestAdditionalPropertiesAsTrue:
    class MyObject(Object):

        options = ObjectOptions(additionalProperties=True)
        value = Property(String())

    @pytest.mark.parametrize(
        "additional_value", ["a string", 1, 3.4, None, True]
    )
    def test_values_are_accepted(self, additional_value: Any):
        with no_raise():
            instance = self.MyObject(
                {"value": "foo", "other_value": additional_value}
            )
        assert instance.additional_properties["other_value"] == additional_value


class TestAdditionalPropertiesAsFalse:
    class MyObject(Object):

        options = ObjectOptions(additionalProperties=False)
        value = Property(String())

    @pytest.mark.parametrize(
        "additional_value", ["a string", 1, 3.4, None, True]
    )
    def test_no_extra_values_are_accepted(self, additional_value: Any):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": "foo", "other_value": additional_value})
