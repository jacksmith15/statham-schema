from typing import Any, Type

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import AnyOf, Array, CompositionElement, OneOf, String
from statham.dsl.property import UNBOUND_PROPERTY
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import Args, no_raise


class TestCompositionInstantiation:
    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf])
    @pytest.mark.parametrize(
        "args", [Args(String()), Args(String(), Array(String()))]
    )
    def test_element_instantiates_with_good_args(
        element: Type[CompositionElement], args: Args
    ):
        with no_raise():
            _ = args.apply(element)

    @staticmethod
    @pytest.mark.parametrize("element", [OneOf, AnyOf])
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


def test_composition_default_keyword():
    element = OneOf(String(), Array(String()), default="foo")
    assert element(NotPassed(), UNBOUND_PROPERTY) == "foo"
    assert element(["foo"], UNBOUND_PROPERTY) == ["foo"]


@pytest.mark.parametrize("element", [OneOf, AnyOf])
def test_composition_annotation(element):
    assert element(String()).annotation == "str"
    assert (
        element(String(), Array(String())).annotation == "Union[str, List[str]]"
    )
