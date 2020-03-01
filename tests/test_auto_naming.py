import pytest

from tests.models.autoname import Autoname


@pytest.mark.github_issue(29)
def test_anonymous_arrays_do_not_overwrite_themselves():
    """Regression test for issue #29."""
    assert Autoname(
        list_of_strings=[{"string_property": "foo"}],
        list_of_integers=[{"integer_property": 1}],
    )


def test_anonymours_any_of_object_items_are_named_correctly():
    assert Autoname(
        list_any_of=[{"string_prop": "foo"}, {"integer_prop": "bar"}]
    )
