import pytest

from statham.validators import has_format


def test_format_checker_warns_if_passed_unknown_format():
    with pytest.warns(RuntimeWarning):
        # False positive
        # pylint: disable=no-value-for-parameter
        has_format("unknown-format")(None, None, "foo")
