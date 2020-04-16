from typing import Any, Dict

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Element, Null
from statham.dsl.helpers import Args
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import no_raise


class TestNullInstantiation:
    @staticmethod
    @pytest.mark.parametrize("args", [Args(), Args(default=None)])
    def test_element_instantiates_with_good_args(args):
        with no_raise():
            _ = args.apply(Null)

    @staticmethod
    @pytest.mark.parametrize("args", [Args(invalid="keyword"), Args("sample")])
    def test_element_raises_on_bad_args(args):
        with pytest.raises(TypeError):
            _ = args.apply(Null)


class TestNullValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [(True, NotPassed()), (True, None), (False, ["foo"]), (False, "")],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(Null(), success, value)


def test_null_default_keyword():
    element = Null(default=None)
    assert element(NotPassed()) is None


def test_null_type_annotation():
    assert Null().annotation == "None"


@pytest.mark.parametrize(
    "element,expected",
    [
        (Null(), {"type": "null"}),
        (Null(default=None), {"type": "null", "default": None}),
    ],
)
def test_null_serialize(element: Element, expected: Dict[str, Any]):
    assert element.serialize() == expected
