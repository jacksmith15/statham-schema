from typing import List

import pytest

from statham.dsl.elements import Array, Object, String
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.property import Property
from statham.orderer import Orderer


class Child(Object):
    value = Property(String())


class Related(Object):
    value = Property(String())


class Parent(Object):
    children = Property(Array(Child))
    related = Property(Related)


@pytest.fixture(scope="session")
def ordered_objects() -> List[ObjectMeta]:
    return [elem for elem in Orderer(Parent)]


def test_correct_number_of_object_elements_produced(
    ordered_objects: List[ObjectMeta]
):
    assert len(ordered_objects) == 3


def test_independent_object_elements_are_declared_first(
    ordered_objects: List[ObjectMeta]
):
    assert set(ordered_objects[:2]) == {Child, Related}


def test_dependent_object_element_is_declared_next(
    ordered_objects: List[ObjectMeta]
):
    assert ordered_objects[2] == Parent
