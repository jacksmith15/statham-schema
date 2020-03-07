from typing import Any

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Integer, Number
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import Args, no_raise


class TestNumericInstantiation:
    @staticmethod
    @pytest.mark.parametrize("elem_type", [Integer, Number])
    @pytest.mark.parametrize(
        "args",
        [
            Args(),
            Args(default=1),
            Args(minimum=2),
            Args(maximum=2),
            Args(exclusiveMinimum=1),
            Args(exclusiveMaximum=3),
            Args(multipleOf=3),
            Args(
                default=1,
                minimum=2,
                maximum=2,
                exclusiveMinimum=1,
                exclusiveMaximum=3,
                multipleOf=3,
            ),
        ],
    )
    def test_element_instantiates_with_good_args(args, elem_type):
        with no_raise():
            _ = args.apply(elem_type)

    @staticmethod
    @pytest.mark.parametrize("elem_type", [Integer, Number])
    @pytest.mark.parametrize("args", [Args(invalid="keyword"), Args("sample")])
    def test_element_raises_on_bad_args(args, elem_type):
        with pytest.raises(TypeError):
            _ = args.apply(elem_type)


class TestIntegerValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 0),
            (True, 12),
            (False, 1.3),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(Integer(), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 2),
            (True, 3),
            (False, 1),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_minimum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Integer(minimum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 2),
            (True, 1),
            (False, 3),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_maximum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Integer(maximum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 3),
            (False, 1),
            (False, 2),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_exclusive_minimum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Integer(exclusiveMinimum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 1),
            (False, 3),
            (False, 2),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_exclusive_maximum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Integer(exclusiveMaximum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (False, 1),
            (True, 2),
            (False, 3),
            (True, 4),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_multiple_of_keyword(
        success: bool, value: Any
    ):
        assert_validation(Integer(multipleOf=2), success, value)


def test_integer_default_keyword():
    element = Integer(default=3)
    assert element(NotPassed()) == 3
    assert element(5) == 5


def test_integer_type_annotation():
    assert Integer().annotation == "int"


class TestNumberValidation:
    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 3.6),
            (True, 12.7),
            (False, 1),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_no_keywords(success: bool, value: Any):
        assert_validation(Number(), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 2.4),
            (True, 3.0),
            (False, 2.1),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_minimum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Number(minimum=2.3), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 2.2),
            (True, 1.1),
            (False, 2.5),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_maximum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Number(maximum=2.3), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 2.0001),
            (False, 1.3),
            (False, 2.0),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_exclusive_minimum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Number(exclusiveMinimum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, 1.999),
            (False, 2.0),
            (False, 2.5),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_exclusive_maximum_keyword(
        success: bool, value: Any
    ):
        assert_validation(Number(exclusiveMaximum=2), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (False, 1.2),
            (True, 2.0),
            (False, 3.0),
            (True, 4.0),
            (False, "foo"),
            (False, ["foo"]),
            (False, None),
        ],
    )
    def test_validation_performs_with_multiple_of_keyword(
        success: bool, value: Any
    ):
        assert_validation(Number(multipleOf=2), success, value)


def test_number_default_keyword():
    element = Number(default=3.3)
    assert element(NotPassed()) == 3.3
    assert element(5.5) == 5.5


def test_number_type_annotation():
    assert Number().annotation == "float"
