from typing import Any, List, Union
import pytest

from statham.schema.constants import Maybe, NotPassed
from statham.schema.elements import (
    Array,
    Integer,
    Nothing,
    Object,
    OneOf,
    String,
)
from statham.schema.property import Property
from statham.schema.exceptions import SchemaDefinitionError, ValidationError
from tests.helpers import no_raise


class StringWrapper(Object):

    value: str = Property(String(minLength=3), required=True)


class ListWrapper(Object):

    list_of_stuff: Maybe[List[Union[StringWrapper, str]]] = Property(
        Array(OneOf(StringWrapper, String(minLength=3)), minItems=1)
    )


class ObjectWrapper(Object):

    obj: StringWrapper = Property(StringWrapper, required=True)


@pytest.mark.parametrize(
    "param", [dict(value="foo"), dict(value="foo", other_value="anything")]
)
def test_string_wrapper_accepts_valid_arguments(param):
    with no_raise():
        _ = StringWrapper(param)


@pytest.mark.parametrize(
    "param", [dict(value="fo"), dict(), dict(value=3), "foo"]
)
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


def test_list_wrapper_assigns_not_passed_correctly():
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
    class DefaultStringWrapper(Object, default=dict(value="bar")):

        value: str = Property(String(minLength=3), required=True)

    def test_that_it_accepts_no_args(self):
        with no_raise():
            instance = self.DefaultStringWrapper()
        assert isinstance(instance, self.DefaultStringWrapper)
        assert instance.value == "bar"

    def test_that_it_accepts_an_arg(self):
        with no_raise():
            instance = self.DefaultStringWrapper({"value": "baz"})
        assert isinstance(instance, self.DefaultStringWrapper)
        assert instance.value == "baz"


class TestSchemaNestedDefault:
    @staticmethod
    def test_default_object_match():
        class DefaultStringWrapper(Object, default=dict(value="bar")):
            value: str = Property(String(), required=True)

        class WrapDefaultObject(Object):
            value = Property(DefaultStringWrapper)

        instance = WrapDefaultObject({})
        assert isinstance(instance.value, DefaultStringWrapper)
        assert instance.value.value == "bar"

    @staticmethod
    def test_default_object_no_match():
        class DefaultStringWrapper(Object, default=dict(other="bar")):
            value: str = Property(String(), required=True)

        class WrapDefaultObject(Object):
            value = Property(DefaultStringWrapper)

        instance = WrapDefaultObject({})
        assert isinstance(instance.value, dict)
        assert instance.value == {"other": "bar"}


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
    class PropertyRename(
        Object, default={"default": "string"}, additionalProperties=False
    ):

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
                __init__ = Property(String())


class TestAdditionalPropertiesAsElement:
    class MyObject(Object, additionalProperties=Integer()):

        value = Property(String())

    def test_valid_instantiation(self):
        with no_raise():
            instance = self.MyObject({"value": "foo", "other_value": 3})
        assert instance.value == "foo"
        with pytest.raises(AttributeError):
            _ = instance.other_value
        assert instance["other_value"] == 3

    def test_additional_value_is_not_accepted_for_declared_value(self):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": 1, "other_value": 3})

    def test_bad_additional_value_is_not_accepted(self):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": "foo", "other_value": "bad"})


class TestAdditionalPropertiesAsTrue:
    class MyObject(Object, additionalProperties=True):

        value = Property(String())

    @pytest.mark.parametrize(
        "additional_value", ["a string", 1, 3.4, None, True]
    )
    def test_values_are_accepted(self, additional_value: Any):
        with no_raise():
            instance = self.MyObject(
                {"value": "foo", "other_value": additional_value}
            )
        with pytest.raises(AttributeError):
            _ = instance.other_value  # type: ignore
        assert instance["other_value"] == additional_value


class TestAdditionalPropertiesAsFalse:
    class MyObject(Object, additionalProperties=False):

        value = Property(String())

    @pytest.mark.parametrize(
        "additional_value", ["a string", 1, 3.4, None, True]
    )
    def test_no_extra_values_are_accepted(self, additional_value: Any):
        with pytest.raises(ValidationError):
            _ = self.MyObject({"value": "foo", "other_value": additional_value})


class TestPatternProperties:
    class MyObject(
        Object,
        patternProperties={"^foo": String(minLength=3), "^(?!foo)": Nothing()},
    ):
        foobar = Property(String())

    @pytest.mark.parametrize(
        "args",
        [
            {},
            {"foobar": "bar"},
            {"foobaz": "baz"},
            {"foobar": "bar", "foobaz": "baz"},
        ],
    )
    def test_that_the_schema_accepts_valid_args(self, args):
        with no_raise():
            instance = self.MyObject(args)
        if "foobar" in args:
            assert instance.foobar == args["foobar"]
            assert args == instance._dict
        else:
            assert instance._dict == {**args, "foobar": NotPassed()}

    @pytest.mark.parametrize(
        "args", [{"foobar": "ar"}, {"foobaz": "az"}, {"barfoo": "foo"}]
    )
    def test_that_the_schema_fails_on_bad_args(self, args):
        with pytest.raises((TypeError, ValidationError)):
            _ = self.MyObject(args)


class TestSizeValidators:
    class MyObject(Object, minProperties=1, maxProperties=2):
        pass

    @pytest.mark.parametrize(
        "data,valid",
        [
            ({}, False),
            ({"foo": "bar"}, True),
            ({"foo": "bar", "qux": "mux"}, True),
            ({"foo": "bar", "qux": "mux", "raz": "maz"}, False),
        ],
    )
    def test_arguments_are_validated(self, data, valid):
        with no_raise() if valid else pytest.raises(
            (TypeError, ValidationError)
        ):
            _ = self.MyObject(data)


class TestPropertyNames:
    class MyObject(Object, propertyNames=String(maxLength=3)):
        pass

    @pytest.mark.parametrize(
        "data,valid",
        [
            ({}, True),
            ({"foo": "bar"}, True),
            ({"foo": "bar", "qux": "mux"}, True),
            ({"foobar": "baz"}, False),
            ({"foobar": "baz", "qux": "mux"}, False),
        ],
    )
    def test_arguments_are_validated(self, data, valid):
        with no_raise() if valid else pytest.raises(
            (TypeError, ValidationError)
        ):
            _ = self.MyObject(data)


class TestConst:
    class MyObject(Object, const={"value": "bar"}):
        value = Property(String())

    @pytest.mark.parametrize(
        "data,valid",
        [
            ({}, False),
            ({"value": "bar"}, True),
            ({"value": "foo"}, False),
            ({"value": "bar", "qux": "mux"}, False),
            ({"qux": "mux"}, False),
        ],
    )
    def test_arguments_are_validated(self, data, valid):
        with no_raise() if valid else pytest.raises(
            (TypeError, ValidationError)
        ):
            _ = self.MyObject(data)

    def test_const_accepts_instance(self):
        instance = self.MyObject({"value": "bar"})
        with no_raise():
            _ = self.MyObject(instance)

    @pytest.mark.xfail(strict=True, reason="Not supported")
    def test_const_accepts_nested_instance(self):
        instance = self.MyObject({"value": "bar"})
        element = Array(self.MyObject, const=[{"value": "bar"}])
        with no_raise():
            _ = element([instance])

    @pytest.mark.xfail(strict=True, reason="Not supported")
    def test_instance_const_accepts_non_instance(self):
        element = Array(self.MyObject, const=[self.MyObject({"value": "bar"})])
        with no_raise():
            _ = element([{"value": "bar"}])


class TestEnum:
    class MyObject(Object, enum=[{"foo": "bar"}, {"qux": "mux"}]):
        pass

    @pytest.mark.parametrize(
        "data,valid",
        [
            ({}, False),
            ({"foo": "bar"}, True),
            ({"qux": "mux"}, True),
            ({"foo": "bar", "qux": "mux"}, False),
            ({"raz": "maz"}, False),
        ],
    )
    def test_arguments_are_validated(self, data, valid):
        with no_raise() if valid else pytest.raises(
            (TypeError, ValidationError)
        ):
            _ = self.MyObject(data)

    def test_enum_accepts_instance(self):
        instance = self.MyObject({"foo": "bar"})
        with no_raise():
            _ = self.MyObject(instance)


class TestRequired:
    class MyObject(Object, required=["value"]):
        pass

    def test_that_missing_value_raises(self):
        with pytest.raises(ValidationError):
            _ = self.MyObject({})

    def test_that_provided_value_succeeds(self):
        with no_raise():
            _ = self.MyObject({"value": 1})


def test_object_classes_accept_custom_attributes():
    with no_raise():

        class MyObject(Object):
            value = Property(String())
            custom = 5

    assert MyObject.custom == 5


def test_object_properties_can_be_fully_overriden():
    class MyObject(Object):
        value = Property(String())

    MyObject.properties = {"other": Property(String())}
    assert "other" in MyObject.properties
    assert MyObject.properties.parent is MyObject
    prop = MyObject.properties["other"]
    assert prop.name == prop.source == "other"
    assert prop.parent is MyObject


def test_element_properties_can_be_edited():
    class MyObject(Object):
        value = Property(String())

    prop = Property(String())
    MyObject.properties["other"] = prop
    assert prop.parent is MyObject
    assert prop.name == prop.source == "other"


class TestObjectInheritance:
    class BaseObject(
        Object, additionalProperties=False, minProperties=0, maxProperties=5
    ):
        value = Property(String())

        custom = 1

    class ChildObject(BaseObject, maxProperties=10):
        other = Property(String())

    def test_that_child_has_both_properties(self):
        assert set(self.ChildObject.properties) == {"value", "other"}

    def test_that_child_object_has_additional_properties(self):
        assert not self.ChildObject.additionalProperties

    def test_that_child_object_inherits_min_properties(self):
        assert self.ChildObject.minProperties == 0

    def test_that_child_object_overwrites_max_properties(self):
        assert self.ChildObject.maxProperties == 10

    def test_that_child_object_inherits_normal_attrs(self):
        assert self.ChildObject.custom == 1

    def test_that_parent_properties_are_correctly_bound(self):
        assert self.BaseObject.properties["value"].parent is self.BaseObject

    def test_that_child_properties_are_correctly_rebound(self):
        assert self.ChildObject.properties["value"].parent is self.ChildObject

    @pytest.mark.parametrize(
        "data,valid",
        [
            ({}, True),
            ({"value": "a string"}, True),
            ({"other": "a string"}, True),
            ({"value": "a string", "other": "another string"}, True),
            ({"value": 1}, False),
            ({"bad": "a string"}, False),
            (
                {
                    "value": "a string",
                    "other": "another string",
                    "bad": "a string",
                },
                False,
            ),
        ],
    )
    def test_that_validation_works_correctly(self, data, valid):
        with pytest.raises(ValidationError) if not valid else no_raise():
            _ = self.ChildObject(data)


def test_object_property_override():
    class BaseObject(Object):
        value = Property(String())

    class ChildObject(BaseObject):
        value = Property(String(maxLength=2))

    with pytest.raises(ValidationError):
        _ = ChildObject(dict(value="a string"))

    with no_raise():
        _ = ChildObject(dict(value="a"))


class TestObjectDescription:
    @staticmethod
    def test_that_description_is_read_from_kwarg():
        class MyObject(Object, description="My description"):
            pass

        assert MyObject.description == "My description"

    @staticmethod
    def test_that_description_is_read_from_docstring():
        class MyObject(Object):
            """My docstring."""

        assert MyObject.description == "My docstring."

    @staticmethod
    def test_that_description_kwargs_takes_precedence():
        class MyObject(Object, description="My description"):
            """My docstring."""

        assert MyObject.description == "My description"
