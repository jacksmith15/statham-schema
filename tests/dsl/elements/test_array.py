from typing import Any

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Array, String
from statham.dsl.property import UNBOUND_PROPERTY
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import Args, no_raise


class TestArrayInstantiation:
    @staticmethod
    @pytest.mark.parametrize(
        "args",
        [
            Args(String()),
            Args(String(), default=[]),
            Args(String(), minItems=1),
            Args(String(), maxItems=3),
            Args(String(), default=[], minItems=1, maxItems=3),
        ],
    )
    def test_element_instantiates_with_good_args(args):
        with no_raise():
            _ = args.apply(Array)

    @staticmethod
    @pytest.mark.parametrize(
        "args", [Args(), Args(String, invalid="keyword"), Args(String, [])]
    )
    def test_element_raises_on_bad_args(args):
        with pytest.raises(TypeError):
            _ = args.apply(Array)


class TestArrayValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, []),
            (True, ["foo"]),
            (True, ["foo", "bar"]),
            (True, NotPassed()),
            (False, "foo"),
            (False, [None]),
            (False, ["foo", None]),
        ],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(Array(String()), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, ["foo"]),
            (True, ["foo", "bar"]),
            (True, NotPassed()),
            (False, "foo"),
            (False, []),
            (False, [None]),
            (False, ["foo", None]),
        ],
    )
    def test_validation_performs_with_min_items_keyword(
        success: bool, value: Any
    ):
        assert_validation(Array(String(), minItems=1), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, []),
            (True, ["foo"]),
            (True, NotPassed()),
            (False, ["foo", "bar"]),
            (False, "foo"),
            (False, [None]),
            (False, ["foo", None]),
        ],
    )
    def test_validation_performs_with_max_items_keyword(
        success: bool, value: Any
    ):
        assert_validation(Array(String(), maxItems=1), success, value)


def test_array_default_keyword():
    element = Array(String(), default=[])
    assert element(NotPassed(), UNBOUND_PROPERTY) == []
    assert element(["foo"], UNBOUND_PROPERTY) == ["foo"]


def test_array_type_annotation():
    assert Array(String()).annotation == "List[str]"
