from itertools import chain
from typing import Any, Type

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import (
    AllOf,
    AnyOf,
    Array,
    CompositionElement,
    Element,
    Not,
    Object,
    OneOf,
    String,
)
from statham.dsl.helpers import Args
from statham.dsl.property import Property
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import no_raise


class TestCompositionInstantiation:
    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf, AllOf])
    @pytest.mark.parametrize(
        "args", [Args(String()), Args(String(), Array(String()))]
    )
    def test_element_instantiates_with_good_args(
        element: Type[CompositionElement], args: Args
    ):
        with no_raise():
            _ = args.apply(element)

    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf, AllOf])
    @pytest.mark.parametrize("args", [Args()])
    def test_element_raises_on_bad_args(
        element: Type[CompositionElement], args: Args
    ):
        with pytest.raises(TypeError):
            _ = args.apply(element)


class CompositionValidation:

    _ELEM_TYPE: Type[CompositionElement]

    @pytest.mark.parametrize(
        "success,value",
        [(True, NotPassed()), (True, "foo"), (False, ["foo"]), (False, None)],
    )
    def test_validation_performs_with_one_schema(
        self, success: bool, value: Any
    ):
        assert_validation(self._ELEM_TYPE(String()), success, value)

    @pytest.mark.parametrize(
        "success,value",
        [(True, NotPassed()), (True, "foo"), (True, ["foo"]), (False, None)],
    )
    def test_validation_performs_with_disjoint_schemas(
        self, success: bool, value: Any
    ):
        assert_validation(
            self._ELEM_TYPE(String(), Array(String())), success, value
        )


class TestOneOfValidation(CompositionValidation):

    _ELEM_TYPE = OneOf

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "fo"),  # Matches first schema
            (True, "foobar"),  # Matches second schema
            (False, "foob"),  # Matches both schemas
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_overlapping_schemas(
        success: bool, value: Any
    ):
        assert_validation(
            OneOf(String(maxLength=5), String(minLength=3)), success, value
        )


class TestAnyOfValidation(CompositionValidation):

    _ELEM_TYPE = AnyOf

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "fo"),  # Matches first schema
            (True, "foobar"),  # Matches second schema
            (True, "foob"),  # Matches both schemas
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_overlapping_schemas(
        success: bool, value: Any
    ):
        assert_validation(
            AnyOf(String(maxLength=5), String(minLength=3)), success, value
        )


class TestAllOfValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (False, "fo"),
            (False, "foobar"),
            (True, "foob"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_behaves_as_expected_on_primitives(
        success: bool, value: Any
    ):
        assert_validation(
            AllOf(String(maxLength=5), String(minLength=3)), success, value
        )

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (False, None),
            (False, ["foo"]),
            (False, "foo"),
            (True, {}),
            (True, {"value": "foo"}),
            (True, {"other_value": "foo"}),
            (True, {"value": "foo", "other_value": "bar"}),
        ],
    )
    def test_validation_behaves_as_expected_on_objects(
        success: bool, value: Any
    ):
        class Foo(Object):
            value = Property(String())

        class Bar(Object):
            other_value = Property(String())

        assert_validation(AllOf(Foo, Bar), success, value)

    @staticmethod
    def test_first_match_is_returned():
        class Foo(Object):
            value = Property(String())

        class Bar(Object):
            other_value = Property(String())

        result = AllOf(Foo, Bar)({"value": "foo", "other_value": "bar"})
        assert isinstance(result, Foo)
        assert result.value == "foo"
        with pytest.raises(AttributeError):
            _ = result.other_value
        assert result["other_value"] == "bar"

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [(True, "foo"), (True, "foo bar"), (False, None), (False, "fo")],
    )
    def test_it_works_with_untyped_elements(success: bool, value: Any):
        assert_validation(AllOf(String(), Element(minLength=3)), success, value)


def test_composition_default_keyword():
    element = OneOf(String(), Array(String()), default="foo")
    assert element(NotPassed()) == "foo"
    assert element(["foo"]) == ["foo"]


@pytest.mark.parametrize("element", [OneOf, AnyOf])
def test_composition_annotation(element):
    assert element(String()).annotation == "str"
    assert (
        element(String(), Array(String())).annotation == "Union[str, List[str]]"
    )


@pytest.mark.parametrize("element", [OneOf, AnyOf])
def test_composition_annotations_are_deduped(element):
    assert element(String(minLength=3), String(maxLength=5)).annotation == "str"


@pytest.mark.parametrize("element", [OneOf, AnyOf])
def test_composition_untyped_annotation_overrides(element):
    assert (
        element(String(minLength=3), Element(maxLength=5)).annotation == "Any"
    )


@pytest.mark.parametrize(
    "element,annotation",
    [
        (AllOf(Element(minLength=3), Element(maxLength=5)), "Any"),
        (AllOf(Element(minLength=3), String(maxLength=5)), "str"),
        (AllOf(String(minLength=3), Element(maxLength=5)), "str"),
        (AllOf(String(minLength=3), Array(String())), "str"),
        (AllOf(Array(String()), String(minLength=3)), "List[str]"),
        (AllOf(OneOf(String(), Array(String())), String()), "str"),
    ],
)
def test_all_of_annotation(element, annotation):
    assert element.annotation == annotation


def test_instantiating_base_element_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        _ = CompositionElement(String())("foo")


def test_default_does_not_affect_sub_schema_attempts():
    element = OneOf(String(), String(default="foo"))
    with no_raise():
        result = element(NotPassed())
    assert result is NotPassed()


def simple_multi_composition_serialize_params():
    return chain.from_iterable(
        [
            [
                (elem(String()), {keyword: [{"type": "string"}]}),
                (
                    elem(String(), default="sample string"),
                    {keyword: [{"type": "string"}], "default": "sample string"},
                ),
                (
                    elem(String(), Array(String())),
                    {
                        keyword: [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                ),
                (
                    elem(String(), Array(String()), default="sample string"),
                    {
                        keyword: [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ],
                        "default": "sample string",
                    },
                ),
            ]
            for elem, keyword in (
                (AnyOf, "anyOf"),
                (AllOf, "allOf"),
                (OneOf, "oneOf"),
            )
        ]
    )


@pytest.mark.parametrize(
    "element,expected",
    [
        (Not(Element()), {"not": {}}),
        (Not(String()), {"not": {"type": "string"}}),
        *simple_multi_composition_serialize_params(),
    ],
)
def test_composition_serialize(element, expected):
    assert element.serialize() == expected
