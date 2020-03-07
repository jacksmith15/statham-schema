from typing import Any

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Boolean
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import Args, no_raise


class TestBooleanInstantiation:
    @staticmethod
    @pytest.mark.parametrize(
        "args", [Args(), Args(default=True), Args(default=False)]
    )
    def test_element_instantiates_with_good_args(args):
        with no_raise():
            _ = args.apply(Boolean)

    @staticmethod
    @pytest.mark.parametrize("args", [Args(invalid="keyword"), Args("sample")])
    def test_element_raises_on_bad_args(args):
        with pytest.raises(TypeError):
            _ = args.apply(Boolean)


class TestBooleanValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, True),
            (True, False),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(Boolean(), success, value)


def test_string_default_keyword():
    element = Boolean(default=False)
    assert element(NotPassed()) is False
    assert element(True) is True


def test_string_type_annotation():
    assert Boolean().annotation == "bool"
