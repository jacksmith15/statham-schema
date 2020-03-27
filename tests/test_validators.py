import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.property import UNBOUND_PROPERTY
from statham.dsl.validation import Format


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
