import pytest

from statham.exceptions import ValidationError
from tests.helpers import no_raise
from tests.models.array_item_validation import Model


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"list_of_strings": []},
        {"list_of_strings": ["A string"]},
        {"list_of_strings": ["A string", "Another string"]},
    ],
)
def test_valid_arguments(kwargs):
    with no_raise():
        _ = Model(**kwargs)


_ARRAY_VALIDATION_MARKS = [pytest.mark.github_issue(34), pytest.mark.xfail]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"list_of_strings": "A string"},
        pytest.param({"list_of_strings": [1]}, marks=_ARRAY_VALIDATION_MARKS),
        pytest.param(
            {"list_of_strings": ["A string", 1]}, marks=_ARRAY_VALIDATION_MARKS
        ),
        pytest.param(
            {"list_of_strings": [1, "A string"]}, marks=_ARRAY_VALIDATION_MARKS
        ),
        pytest.param(
            {"list_of_strings": [None]}, marks=_ARRAY_VALIDATION_MARKS
        ),
    ],
)
def test_invalid_arguments(kwargs):
    with pytest.raises(ValidationError):
        _ = Model(**kwargs)
