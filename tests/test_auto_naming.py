from typing import List, Tuple, Type

import pytest

from tests.models.autoname import Autoname, ListAnyOfItem0, ListAnyOfItem1


@pytest.mark.github_issue(29)
def test_anonymous_arrays_do_not_overwrite_themselves():
    """Regression test for issue #29."""
    assert Autoname(
        list_of_strings=[{"string_property": "foo"}],
        list_of_integers=[{"integer_property": 1}],
    )


class TestAnonymousAnyOfObjects:
    @staticmethod
    @pytest.fixture(scope="class")
    def instance() -> Autoname:
        return Autoname(
            list_any_of=[{"string_prop": "foo"}, {"integer_prop": 1}]
        )

    @staticmethod
    def test_successful_top_level_instantiation(instance: Autoname):
        assert isinstance(instance, Autoname)

    PARAMS: List[Tuple[int, Type]] = [(0, ListAnyOfItem0), (1, ListAnyOfItem1)]

    @staticmethod
    @pytest.mark.parametrize("index,model", PARAMS)
    def test_successful_attribute_instantiation(
        instance: Autoname, index: int, model: Type
    ):
        assert isinstance(instance.list_any_of, list)
        assert isinstance(instance.list_any_of[index], model)
