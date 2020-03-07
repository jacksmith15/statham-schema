from typing import Any

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import String
from statham.dsl.property import UNBOUND_PROPERTY
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import Args, no_raise


class TestStringInstantiation:
    @staticmethod
    @pytest.mark.parametrize(
        "args",
        [
            Args(),
            Args(default="sample"),
            Args(format="my_format"),
            Args(pattern=".*"),
            Args(minLength=1),
            Args(maxLength=3),
            Args(
                default="sample",
                format="my_format",
                pattern=".*",
                minLength=1,
                maxLength=3,
            ),
        ],
    )
    def test_element_instantiates_with_good_args(args):
        with no_raise():
            _ = args.apply(String)

    @staticmethod
    @pytest.mark.parametrize("args", [Args(invalid="keyword"), Args("sample")])
    def test_element_raises_on_bad_args(args):
        with pytest.raises(TypeError):
            _ = args.apply(String)


class TestStringValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "foo"),
            (True, ""),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(String(), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "ed5d1f26-f1c0-46bf-a518-72d5894b0253"),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_format_keyword(success: bool, value: Any):
        assert_validation(String(format="uuid"), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "F-123"),
            (True, "R-456"),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_pattern_keyword(
        success: bool, value: Any
    ):
        assert_validation(String(pattern=r"(F|R)-\d{3}"), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "foo"),
            (True, "fo"),
            (False, "f"),
            (False, ""),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_min_length_keyword(
        success: bool, value: Any
    ):
        assert_validation(String(minLength=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, "fo"),
            (True, "f"),
            (True, ""),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_max_length_keyword(
        success: bool, value: Any
    ):
        assert_validation(String(maxLength=2), success, value)


def test_string_default_keyword():
    element = String(default="foo")
    assert element(NotPassed(), UNBOUND_PROPERTY) == "foo"
    assert element("bar", UNBOUND_PROPERTY) == "bar"


def test_string_type_annotation():
    assert String().annotation == "str"
