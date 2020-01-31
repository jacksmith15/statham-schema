import pytest

from statham.exceptions import ValidationError
from tests.models.any_of import FooStringMinLength, BarIntegerFooString, Model


class TestPrimitiveAnyOf:
    @staticmethod
    def test_model_instantiates_with_no_args():
        assert Model()

    @staticmethod
    def test_primitive_any_of_accepts_string_type():
        assert Model(primitive="foo").primitive == "foo"

    @staticmethod
    def test_primitive_any_of_accepts_integer_type():
        assert Model(primitive=3).primitive == 3

    @staticmethod
    def test_primitive_any_of_rejects_other_type():
        with pytest.raises(ValidationError):
            Model(primitive={"foo": "bar"})

    @staticmethod
    def test_primitive_validation_is_applied_to_string_type():
        with pytest.raises(ValidationError):
            Model(primitive="fo")

    @staticmethod
    def test_primitive_validation_is_applied_to_integer_type():
        with pytest.raises(ValidationError):
            Model(primitive=1)


class TestObjectAnyOf:
    @staticmethod
    def test_input_matching_only_first_schema_resolves_to_that_type():
        instance = Model(objects={"foo": "barbaz"})
        assert isinstance(instance.objects, FooStringMinLength)
        assert instance.objects.foo == "barbaz"

    @staticmethod
    def test_input_matching_only_second_schema_resolves_to_that_type():
        instance = Model(objects={"bar": 1, "foo": 2})
        assert isinstance(instance.objects, BarIntegerFooString)
        assert instance.objects.bar == 1

    @staticmethod
    def test_input_matching_both_schemas_resolves_to_first_type():
        instance = Model(objects={"foo": "bar"})
        assert isinstance(instance.objects, FooStringMinLength)
        assert instance.objects.foo == "bar"

    @staticmethod
    def test_input_matching_neither_schemas_raises_validation_error():
        with pytest.raises(ValidationError) as excinfo:
            Model(objects={"foo": "barbaz", "bar": 1})
        assert "Does not match any accepted model." in str(excinfo.value)
