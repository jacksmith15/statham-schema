import pytest

from tests.models.multi_object import Category, Child, Model


def test_required_properties_validate_correctly():
    with pytest.raises(TypeError):
        _ = Category()


def test_category_may_be_passed_to_both_other_models():
    category = Category(required_name="foo")
    assert Model(category=category)
    assert Child(category=category)


def test_full_instantiation():
    category = [dict(required_name=f"category {i}") for i in range(3)]
    assert Model(
        children=[
            dict(name="child 1", category=category[0]),
            dict(name="child 2", category=category[1]),
        ],
        category=category[2],
    )
