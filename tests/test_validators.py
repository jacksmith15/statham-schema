import pytest

from statham.schema.constants import NotPassed
from statham.schema.elements.base import UNBOUND_PROPERTY
from statham.schema.validation import Format, MultipleOf, Validator
from tests.helpers import no_raise


def test_format_checker_warns_if_passed_unknown_format():
    with pytest.warns(RuntimeWarning):
        # False positive
        # pylint: disable=no-value-for-parameter
        Format("unknown-format")("foo", UNBOUND_PROPERTY)


class TestNotPassed:
    @staticmethod
    def test_not_passed_bool_value():
        assert not NotPassed()

    @staticmethod
    def test_not_passed_singleton():
        assert NotPassed() is NotPassed()

    @staticmethod
    def test_not_passed_repr():
        assert repr(NotPassed()) == "NotPassed"


@pytest.mark.parametrize("args", [[], ["uuid", "date-time"]])
def test_that_validator_fails_if_bad_number_of_arguments_is_passed(args):
    with pytest.raises(TypeError):
        Format(*args)


def test_that_base_validator_does_not_raise():
    with no_raise():
        Validator()(None, None)


def test_multiple_of_rounding():
    validator = MultipleOf(0.0001)
    with no_raise():
        validator(0.0075, None)
