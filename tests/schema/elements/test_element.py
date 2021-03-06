from typing import Any, Iterator, List, NamedTuple, Tuple
import pytest

from statham.schema.constants import NotPassed
from statham.schema.elements import Element, Nothing, String
from statham.schema.elements.base import _AnonymousObject
from statham.schema.exceptions import SchemaDefinitionError, ValidationError
from statham.schema.property import _Property
from tests.helpers import no_raise


class Case(NamedTuple):
    element: Element
    good: List[Any]
    bad: List[Any]


CASES = [
    Case(
        element=Element(),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {"foo": "bar"},
            ["foo", 1],
        ],
        bad=[],
    ),
    Case(
        element=Element(minItems=3),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", 1, 5]],
        bad=[[], [1, 2]],
    ),
    Case(
        element=Element(minimum=3),
        good=[None, NotPassed(), True, 3, 4.2, "foo", {}, ["foo", 1]],
        bad=[2, 2.1],
    ),
    Case(
        element=Element(minLength=3),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", 1]],
        bad=["ab", ""],
    ),
    Case(
        element=Element(minItems=3, minimum=3, minLength=3),
        good=[None, NotPassed(), True, 3, 4.2, "foo", {}, ["foo", 1, 5]],
        bad=[[], [1, 2], 2, 2.1, "ab", ""],
    ),
    Case(
        element=Element(items=String()),
        good=[None, NotPassed(), True, 1, 1.2, "foo", {}, ["foo", "b", ""]],
        bad=[["foo", 1], [1]],
    ),
    Case(
        element=Element(properties={"baz": _Property(String())}),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {},
            {"baz": "bar"},
            {"foo": "bar"},
            {"foo": 1, "baz": "bar"},
            ["foo", 1],
        ],
        bad=[{"baz": 1}],
    ),
    Case(
        element=Element(properties={"baz": _Property(String(), required=True)}),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {"baz": "bar"},
            {"foo": 1, "baz": "bar"},
            ["foo", 1],
        ],
        bad=[{}, {"foo": "bar"}, {"baz": 1}],
    ),
    Case(
        element=Element(
            properties={"baz": _Property(String())}, required=["baz"]
        ),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {"baz": "bar"},
            {"foo": 1, "baz": "bar"},
            ["foo", 1],
        ],
        bad=[{}, {"foo": "bar"}, {"baz": 1}],
    ),
    Case(
        element=Element(
            properties={"baz": _Property(String())}, additionalProperties=False
        ),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {},
            {"baz": "bar"},
            ["foo", 1],
        ],
        bad=[{"foo": 1, "baz": "bar"}, {"foo": "bar"}, {"baz": 1}],
    ),
    Case(
        element=Element(additionalProperties=String()),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {},
            {"baz": "bar"},
            {"foo": "bar"},
            ["foo", 1],
        ],
        bad=[{"foo": 1, "baz": "bar"}, {"baz": 1}],
    ),
    Case(
        element=Element(required=["baz"]),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {"baz": "bar"},
            {"foo": 1, "baz": "bar"},
            {"baz": 1},
            ["foo", 1],
        ],
        bad=[{}, {"foo": "bar"}],
    ),
    Case(
        element=Nothing(),
        good=[NotPassed()],
        bad=[None, True, 1, 1.2, "foo", {"foo": "bar"}, ["foo", 1]],
    ),
    Case(
        element=Element(const="foo"),
        good=["foo", NotPassed()],
        bad=[None, True, 1, 1.2, "bar", {"foo": "bar"}, ["foo", 1]],
    ),
    Case(
        element=Element(contains=String()),
        good=[
            None,
            NotPassed(),
            True,
            1,
            1.2,
            "foo",
            {"foo": "bar"},
            ["foo"],
            ["foo", 1],
            ["foo", 1, "bar"],
        ],
        bad=[[], [1, 2, 3]],
    ),
    Case(
        element=Element(enum=[1, 2, 3, 4]),
        good=[NotPassed(), 1, 2, 3, 4],
        bad=[None, True, 5, 1.2, "foo", {"foo": "bar"}, ["foo", 1]],
    ),
]


def to_test_params(cases: List[Case]) -> Iterator[Tuple[Element, Any, bool]]:
    for case in cases:
        for value in case.good:
            yield (case.element, value, False)
        for value in case.bad:
            yield (case.element, value, True)


@pytest.mark.parametrize("element,value,error", list(to_test_params(CASES)))
def test_element_validation_is_performed_on_given_types(element, value, error):
    with pytest.raises(ValidationError) if error else no_raise():
        element(value)


class TestAnonymousObject:
    @staticmethod
    @pytest.fixture(scope="class")
    def result():
        return Element()(
            {
                "string": "bar",
                "list": [{"string": "bar"}],
                "object": {"string": "bar"},
            }
        )

    @staticmethod
    def test_that_result_is_correct_type(result):
        assert isinstance(result, _AnonymousObject)

    @staticmethod
    def test_that_string_attribute_is_unchanged(result):
        assert result.string == "bar"

    @staticmethod
    def test_that_nested_object_is_also_anonymous_object(result):
        assert isinstance(result.object, _AnonymousObject)
        assert result.object.string == "bar"

    @staticmethod
    def test_that_nested_list_contains_nested_object(result):
        assert isinstance(result.list, list)
        assert isinstance(result.list[0], _AnonymousObject)
        assert result.list[0].string == "bar"

    @staticmethod
    def test_that_attributes_can_be_set(result):
        result.new = "foo"
        assert result.new == "foo"


def test_nothing_element_is_falsey():
    assert not Nothing()


def test_nothing_element_annotation_is_none():
    assert Nothing().annotation == "None"


def test_required_renamed_property():
    element = Element(
        properties={
            "class_": _Property(Element(), source="class", required=True)
        }
    )
    with no_raise():
        _ = element({"class": None})


class TestPropertyBinding:
    @staticmethod
    @pytest.mark.parametrize(
        "initial", (NotPassed(), {"value": _Property(Element())})
    )
    def test_element_properties_can_be_fully_overriden(initial):
        element = Element(properties=initial)
        element.properties = {"other": _Property(Element())}
        assert "other" in element.properties
        assert element.properties.parent is element
        prop = element.properties["other"]
        assert prop.name == prop.source == "other"
        assert prop.parent is element

    @staticmethod
    def test_full_override_with_bad_property_raises():
        element = Element(properties={"value": _Property(Element())})
        with pytest.raises(SchemaDefinitionError):
            element.properties = {"other": 0}

    @staticmethod
    def test_element_properties_can_be_edited():
        element = Element(properties={"value": _Property(Element())})
        prop = _Property(Element())
        element.properties["other"] = prop
        assert prop.parent is element
        assert prop.name == prop.source == "other"

    @staticmethod
    def test_setting_a_bad_property_raises():
        element = Element(properties={"value": _Property(Element())})
        with pytest.raises(SchemaDefinitionError):
            element.properties["other"] = 0
