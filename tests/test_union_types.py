from typing import Dict, List, Optional, Tuple, Type

import pytest

from statham.exceptions import ValidationError
from tests.helpers import abstract_model_instantiate_test
from tests.models.union_types import Model


FIELD_VALIDATION_PARAMS: List[
    Tuple[Dict, Optional[Type[Exception]], Optional[str]]
] = [
    ({}, None, None),
    (
        {"number_integer": None},
        ValidationError,
        "Must be of type (int, float).",
    ),
    (
        {"number_integer": 1},
        ValidationError,
        "Must be greater than or equal to 2.5.",
    ),
    (
        {"number_integer": 1.5},
        ValidationError,
        "Must be greater than or equal to 2.5.",
    ),
    ({"number_integer": 6}, ValidationError, "Must be strictly less than 5."),
    ({"number_integer": 5.4}, ValidationError, "Must be strictly less than 5."),
    ({"number_integer": 3}, None, None),
    ({"number_integer": 3.5}, None, None),
    ({"string_integer": None}, ValidationError, "Must be of type (int, str)."),
    (
        {"string_integer": 5},
        ValidationError,
        "Must be greater than or equal to 1970.",
    ),
    (
        {"string_integer": 2060},
        ValidationError,
        "Must be strictly less than 2050.",
    ),
    (
        {"string_integer": "foobar"},
        ValidationError,
        "Must match format described by 'date-time'.",
    ),
    ({"string_integer": 1984}, None, None),
    ({"string_integer": "1984"}, None, None),
]


@pytest.mark.parametrize(
    "kwargs,exception_type,exception_msg", FIELD_VALIDATION_PARAMS
)
def test_number_integer_validation(
    kwargs: Dict,
    exception_type: Optional[Type[Exception]],
    exception_msg: Optional[str],
):
    abstract_model_instantiate_test(
        Model, kwargs, exception_type, exception_msg
    )
