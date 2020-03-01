from typing import Optional

import pytest

from statham.exceptions import ValidationError
from tests.models.one_of import (
    Model,
    OtherStringWrapper,
    StringWrapper,
    StringAndIntegerWrapper,
)


class TestPrimitiveOneOf:
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


class TestObjectOneOf:
    @staticmethod
    def test_input_matching_only_first_schema_resolves_to_that_type():
        instance = Model(objects={"string_prop": "barbaz"})
        assert isinstance(instance.objects, StringWrapper)
        assert instance.objects.string_prop == "barbaz"

    @staticmethod
    @pytest.mark.parametrize("string_prop", ["fo", "foo"])
    def test_input_matching_only_second_schema_resolves_to_that_type(
        string_prop: Optional[str]
    ):
        instance = Model(
            objects={"integer_prop": 1, "string_prop": string_prop}
        )
        assert isinstance(instance.objects, StringAndIntegerWrapper)
        assert instance.objects.integer_prop == 1

    @staticmethod
    def test_input_matching_both_schemas_raises_validation_error():
        with pytest.raises(ValidationError) as excinfo:
            _ = Model(objects={"string_prop": "bar"})
        assert (
            "Matches multiple possible models. Must only match one."
        ) in str(excinfo.value)

    @staticmethod
    def test_input_matching_neither_schemas_raises_validation_error():
        with pytest.raises(ValidationError) as excinfo:
            Model(objects={"string_prop": "barbaz", "integer_prop": 1})
        assert "Does not match any accepted model." in str(excinfo.value)


class TestMixedOneOf:
    @staticmethod
    def test_mixed_schema_accepts_primitive_string():
        instance = Model(mixed="foo")
        assert instance.mixed == "foo"

    @staticmethod
    def test_mixed_schema_accepts_string_wrapper():
        instance = Model(mixed={"string_prop": "foo"})
        assert isinstance(instance.mixed, OtherStringWrapper)
        assert instance.mixed.string_prop == "foo"

    @staticmethod
    def test_bad_primitive_raises_validation_error():
        with pytest.raises(ValidationError):
            _ = Model(mixed=1)

    @staticmethod
    def test_bad_object_raises_validation_error():
        with pytest.raises(ValidationError):
            _ = Model(mixed={"string_prop": 1})
