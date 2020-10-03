import pytest

from statham.schema.exceptions import ValidationError
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
        _ = Model(kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"list_of_strings": "A string"},
        {"list_of_strings": [1]},
        {"list_of_strings": ["A string", 1]},
        {"list_of_strings": [1, "A string"]},
        {"list_of_strings": [None]},
    ],
)
def test_invalid_arguments(kwargs):
    with pytest.raises(ValidationError):
        _ = Model(kwargs)
