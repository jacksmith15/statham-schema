from typing import Any, Dict, List, Optional, Tuple, Type

import pytest

from statham.exceptions import ValidationError
from tests.helpers import abstract_model_instantiate_test
from tests.models.field_validation import Model


FIELD_VALIDATION_PARAMS: List[
    Tuple[Dict, Optional[Type[Exception]], Optional[str]]
] = [
    ({}, None, None),
    ({"string_no_validation": "foo"}, None, None),
    ({"string_no_validation": None}, ValidationError, "Must be of type (str)."),
    (
        {"string_format_uuid": "3ffaeb95-d650-4ad8-9a08-9b4fb246c2ed"},
        None,
        None,
    ),
    (
        {"string_format_uuid": "foo"},
        ValidationError,
        "Must match format described by 'uuid'.",
    ),
    ({"string_format_date_time": "2019-11-17T18:03:01.988614"}, None, None),
    (
        {"string_format_date_time": "foo"},
        ValidationError,
        "Must match format described by 'date-time'.",
    ),
    ({"string_pattern": "foo-baz"}, None, None),
    (
        {"string_pattern": "baz-foo"},
        ValidationError,
        "Must match regex pattern '^(foo|bar).*'.",
    ),
    (
        {"string_minLength": "fo"},
        ValidationError,
        "Must be at least 3 characters long.",
    ),
    ({"string_minLength": "foo"}, None, None),
    ({"string_minLength": "foob"}, None, None),
    ({"string_maxLength": "fo"}, None, None),
    ({"string_maxLength": "foo"}, None, None),
    (
        {"string_maxLength": "foob"},
        ValidationError,
        "Must be at most 3 characters long.",
    ),
    ({"integer_no_validation": 1}, None, None),
    (
        {"integer_no_validation": None},
        ValidationError,
        "Must be of type (int).",
    ),
    (
        {"integer_minimum": 2},
        ValidationError,
        "Must be greater than or equal to 3.",
    ),
    ({"integer_minimum": 3}, None, None),
    ({"integer_minimum": 4}, None, None),
    (
        {"integer_exclusiveMinimum": 2},
        ValidationError,
        "Must be strictly greater than 3.",
    ),
    (
        {"integer_exclusiveMinimum": 3},
        ValidationError,
        "Must be strictly greater than 3.",
    ),
    ({"integer_exclusiveMinimum": 4}, None, None),
    ({"integer_maximum": 2}, None, None),
    ({"integer_maximum": 3}, None, None),
    (
        {"integer_maximum": 4},
        ValidationError,
        "Must be less than or equal to 3.",
    ),
    ({"integer_exclusiveMaximum": 2}, None, None),
    (
        {"integer_exclusiveMaximum": 3},
        ValidationError,
        "Must be strictly less than 3.",
    ),
    (
        {"integer_exclusiveMaximum": 4},
        ValidationError,
        "Must be strictly less than 3.",
    ),
    ({"integer_multipleOf": 4}, None, None),
    ({"integer_multipleOf": 5}, ValidationError, "Must be a multiple of 2."),
    ({"number_no_validation": 2.5}, None, None),
    (
        {"number_no_validation": None},
        ValidationError,
        "Must be of type (float).",
    ),
    (
        {"number_minimum": 2.4},
        ValidationError,
        "Must be greater than or equal to 2.5.",
    ),
    ({"number_minimum": 2.5}, None, None),
    ({"number_minimum": 2.6}, None, None),
    (
        {"number_exclusiveMinimum": 2.4},
        ValidationError,
        "Must be strictly greater than 2.5.",
    ),
    (
        {"number_exclusiveMinimum": 2.5},
        ValidationError,
        "Must be strictly greater than 2.5.",
    ),
    ({"number_exclusiveMinimum": 2.6}, None, None),
    ({"number_maximum": 2.4}, None, None),
    ({"number_maximum": 2.5}, None, None),
    (
        {"number_maximum": 2.6},
        ValidationError,
        "Must be less than or equal to 2.5.",
    ),
    ({"number_exclusiveMaximum": 2.4}, None, None),
    (
        {"number_exclusiveMaximum": 2.5},
        ValidationError,
        "Must be strictly less than 2.5.",
    ),
    (
        {"number_exclusiveMaximum": 2.6},
        ValidationError,
        "Must be strictly less than 2.5.",
    ),
    ({"number_multipleOf": 7.5}, None, None),
    ({"number_multipleOf": 7.6}, ValidationError, "Must be a multiple of 2.5."),
    ({"boolean_no_validation": True}, None, None),
    (
        {"boolean_no_validation": None},
        ValidationError,
        "Must be of type (bool).",
    ),
    ({"null_no_validation": None}, None, None),
    ({"null_no_validation": 1}, ValidationError, "Must be of type (NoneType)."),
]


@pytest.mark.parametrize(
    "kwargs,exception_type,exception_msg", FIELD_VALIDATION_PARAMS
)
def test_field_validation(
    kwargs: Dict,
    exception_type: Optional[Type[Exception]],
    exception_msg: Optional[str],
):
    abstract_model_instantiate_test(
        Model, kwargs, exception_type, exception_msg
    )


@pytest.fixture(scope="module")
def instance():
    return Model()


@pytest.mark.parametrize(
    "attribute,expected_value",
    [
        ("string_default", "foo"),
        ("integer_default", 1),
        ("number_default", 1.5),
        ("boolean_default", True),
    ],
)
def test_default_values(instance: Model, attribute: str, expected_value: Any):
    assert getattr(instance, attribute) == expected_value
