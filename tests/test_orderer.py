from collections import deque
from typing import List

import pytest

from statham.dsl.elements import Array, Element, Object, String
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.property import Property
from statham.orderer import Orderer


class Child(Object):
    value = Property(String())


class Related(Object):
    value = Property(String())


class Parent(Object):
    children = Property(Array(Child))
    related = Property(Related)


class TestSimpleOrdering:
    @staticmethod
    @pytest.fixture(scope="class")
    def ordered_objects() -> List[ObjectMeta]:
        return [elem for elem in Orderer(Parent)]

    @staticmethod
    def test_correct_number_of_object_elements_produced(
        ordered_objects: List[ObjectMeta]
    ):
        assert len(ordered_objects) == 3

    @staticmethod
    def test_independent_object_elements_are_declared_first(
        ordered_objects: List[ObjectMeta]
    ):
        assert set(ordered_objects[:2]) == {Child, Related}

    @staticmethod
    def test_dependent_object_element_is_declared_next(
        ordered_objects: List[ObjectMeta]
    ):
        assert ordered_objects[2] == Parent


class Other(Object):

    value = Property(Child)


class TestMultipleEntryPointOrdering:
    @staticmethod
    @pytest.fixture(scope="class")
    def ordered_objects() -> List[ObjectMeta]:
        return [elem for elem in Orderer(Parent, Other, Child)]

    @staticmethod
    def test_that_there_are_the_correct_number_of_items(
        ordered_objects: List[ObjectMeta]
    ):
        assert len(ordered_objects) == 4

    @staticmethod
    def test_that_the_most_depended_upon_item_comes_first(
        ordered_objects: List[ObjectMeta]
    ):
        assert ordered_objects[0] is Child

    @staticmethod
    def test_that_parent_is_declared_after_related(
        ordered_objects: List[ObjectMeta]
    ):
        ordered = {elem: idx for idx, elem in enumerate(ordered_objects)}
        assert ordered[Parent] > ordered[Related]


def test_orderer_detects_additional_properties_dependencies():
    class AdditionalPropertiesParent(Object, additionalProperties=Child):
        pass

    assert list(Orderer(AdditionalPropertiesParent)) == [
        Child,
        AdditionalPropertiesParent,
    ]


def test_orderer_detects_pattern_properties_dependencies():
    class PatternPropertiesParent(Object, patternProperties={"^foo": Child}):
        pass

    assert list(Orderer(PatternPropertiesParent)) == [
        Child,
        PatternPropertiesParent,
    ]


def test_orderer_detects_property_names_dependencies():
    # This is nonsensical - but technically JSON Schema supports it.
    class PropertyNamesParent(Object, propertyNames=Child):
        pass

    assert list(Orderer(PropertyNamesParent)) == [Child, PropertyNamesParent]


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(additionalProperties=Child),
        dict(properties={"value": Property(Child)}),
        dict(items=Child),
        dict(patternProperties={"^foo": Child}),
        dict(propertyNames=Child),
    ],
)
def test_orderer_detects_untyped_object_dependencies(kwargs):
    class UntypedParent(Object):
        value = Property(Element(**kwargs))

    assert list(Orderer(UntypedParent)) == [Child, UntypedParent]
