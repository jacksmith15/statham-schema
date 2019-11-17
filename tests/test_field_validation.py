from typing import Dict, List, Optional, Tuple, Type

import pytest

from tests.models.field_validation import Model


FIELD_VALIDATION_PARAMS: List[Tuple[Dict, Optional[Type[Exception]]]] = [
    ({}, None),
    ({"string_no_validation": "foo"}, None),
    ({"string_no_validation": None}, TypeError),
    # The following are not yet implemented.
    # ({"string_format_uuid": "3ffaeb95-d650-4ad8-9a08-9b4fb246c2ed"}, None),
    # ({"string_format_uuid": "foo"}, ValueError),
    # ({"string_format_date_time": "2019-11-17T18:03:01.988614"}, None),
    # ({"string_format_date_time": "foo"}, ValueError),
    ({"string_pattern": "foo-baz"}, None),
    ({"string_pattern": "baz-foo"}, ValueError),
    ({"string_minLength": "fo"}, ValueError),
    ({"string_minLength": "foo"}, None),
    ({"string_minLength": "foob"}, None),
    ({"string_maxLength": "fo"}, None),
    ({"string_maxLength": "foo"}, None),
    ({"string_maxLength": "foob"}, ValueError),
    ({"integer_no_validation": 1}, None),
    ({"integer_no_validation": None}, TypeError),
    ({"integer_minimum": 2}, ValueError),
    ({"integer_minimum": 3}, None),
    ({"integer_minimum": 4}, None),
    ({"integer_exclusiveMinimum": 2}, ValueError),
    ({"integer_exclusiveMinimum": 3}, ValueError),
    ({"integer_exclusiveMinimum": 4}, None),
    ({"integer_maximum": 2}, None),
    ({"integer_maximum": 3}, None),
    ({"integer_maximum": 4}, ValueError),
    ({"integer_exclusiveMaximum": 2}, None),
    ({"integer_exclusiveMaximum": 3}, ValueError),
    ({"integer_exclusiveMaximum": 4}, ValueError),
    ({"integer_multipleOf": 4}, None),
    ({"integer_multipleOf": 5}, ValueError),
    ({"number_no_validation": 2.5}, None),
    ({"number_no_validation": None}, TypeError),
    ({"number_minimum": 2.4}, ValueError),
    ({"number_minimum": 2.5}, None),
    ({"number_minimum": 2.6}, None),
    ({"number_exclusiveMinimum": 2.4}, ValueError),
    ({"number_exclusiveMinimum": 2.5}, ValueError),
    ({"number_exclusiveMinimum": 2.6}, None),
    ({"number_maximum": 2.4}, None),
    ({"number_maximum": 2.5}, None),
    ({"number_maximum": 2.6}, ValueError),
    ({"number_exclusiveMaximum": 2.4}, None),
    ({"number_exclusiveMaximum": 2.5}, ValueError),
    ({"number_exclusiveMaximum": 2.6}, ValueError),
    ({"number_multipleOf": 7.5}, None),
    ({"number_multipleOf": 7.6}, ValueError),
    ({"boolean_no_validation": True}, None),
    ({"boolean_no_validation": None}, TypeError),
]


@pytest.mark.parametrize("kwargs,exception", FIELD_VALIDATION_PARAMS)
def test_field_validation(kwargs: Dict, exception: Optional[Type[Exception]]):
    if not exception:
        try:
            assert Model(**kwargs)
        except Exception as exc:
            raise AssertionError(f"Failed field validation: {kwargs}") from exc
        return
    with pytest.raises(
        Exception, message=f"Failed field validation: {kwargs}"
    ) as excinfo:
        Model(**kwargs)
    assert excinfo.type is exception


def test_default():
    pass
