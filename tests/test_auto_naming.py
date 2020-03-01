import pytest

from tests.models.autoname import Autoname


@pytest.mark.github_issue(29)
def test_anonymous_arrays_do_not_overwrite_themselves():
    """Regression test for issue #29."""
    assert Autoname(
        list_of_strings=[{"string_property": "foo"}],
        list_of_integers=[{"integer_property": 1}],
    )
