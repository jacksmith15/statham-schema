from typing import Dict

import pytest

from jsonschema_objects.dependency_resolver import ClassDependencyResolver
from jsonschema_objects.models import ObjectSchema


@pytest.fixture()
def ordered_schema_titles(schema_model: ObjectSchema) -> Dict[str, int]:
    return {
        schema.title: idx
        for idx, schema in enumerate(ClassDependencyResolver(schema_model))
    }


def test_that_the_expected_number_of_schemas_are_retrieved(
    ordered_schema_titles: Dict[str, int]
):
    assert len(ordered_schema_titles) == 3


def test_that_most_dependent_item_is_declared_last(
    ordered_schema_titles: Dict[str, int]
):
    assert ordered_schema_titles["Parent"] == 2


def test_that_items_with_no_dependencies_are_declared_first(
    ordered_schema_titles: Dict[str, int]
):
    assert {
        ordered_schema_titles[title] for title in ["ChildItem", "RelatedItem"]
    } == {0, 1}
