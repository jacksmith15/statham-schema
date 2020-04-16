from typing import Any, Dict

import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Array, Element, Integer, Object, String
from statham.dsl.helpers import Args
from statham.dsl.property import Property
from tests.dsl.elements.helpers import assert_validation
from tests.helpers import no_raise


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

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, []),
            (True, ["foo"]),
            (True, ["foo", "bar"]),
            (True, [True, 1]),
            (False, [True, True]),
            (False, ["foo", "foo"]),
            (False, ["foo", "bar", "foo"]),
            (False, "foo"),
        ],
    )
    def test_validation_performs_with_unique_items_keyword(
        success: bool, value: Any
    ):
        assert_validation(Array(Element(), uniqueItems=True), success, value)

    @staticmethod
    @pytest.mark.parametrize(
        "success,value",
        [
            (True, NotPassed()),
            (True, ["foo"]),
            (True, ["foo", 1]),
            (True, ["foo", 1, "bar"]),
            (False, []),
            (False, [True, True]),
            (False, [1, 2, 3]),
            (False, "foo"),
        ],
    )
    def test_validation_performs_with_contains_keyword(
        success: bool, value: Any
    ):
        assert_validation(Array(Element(), contains=String()), success, value)


def test_array_default_keyword():
    element = Array(String(), default=[])
    assert element(NotPassed()) == []
    assert element(["foo"]) == ["foo"]


@pytest.mark.parametrize(
    "element,annotation",
    [
        (Array(String()), "List[str]"),
        (Array(Element()), "List[Any]"),
        (Array([String(), Element()]), "List[Any]"),
        (Array([String(), String()], additionalItems=False), "List[str]"),
        (Array([String(), Element()], additionalItems=False), "List[Any]"),
        (
            Array([String(), String()], additionalItems=Integer()),
            "List[Union[str, int]]",
        ),
        (
            Array([String(), Integer()], additionalItems=False),
            "List[Union[str, int]]",
        ),
        (Array([], additionalItems=False), "List"),
    ],
)
def test_array_type_annotation(element: Array, annotation: str):
    assert element.annotation == annotation
    assert Array(String()).annotation == "List[str]"


class TestArrayDefault:
    class Foo(Object):
        value = Property(String(), required=True)

    def test_array_default_match(self):
        element = Array(self.Foo, default=[{"value": "foo"}])
        instance = element(NotPassed())
        assert instance == [self.Foo({"value": "foo"})]

    def test_array_default_no_match(self):
        element = Array(self.Foo, default=[None])
        assert element(NotPassed()) == [None]

    def test_array_default_no_match_object(self):
        element = Array(self.Foo, default=[{"other": "foo"}])
        instance = element(NotPassed())
        assert instance == [{"other": "foo"}]


@pytest.mark.parametrize(
    "element,expected",
    [
        (Array(Element()), {"type": "array", "items": {}}),
        (Array(String()), {"type": "array", "items": {"type": "string"}}),
        (
            Array(
                String(),
                default=["foo", "bar"],
                minItems=1,
                maxItems=3,
                contains=String(),
                uniqueItems=True,
            ),
            {
                "type": "array",
                "items": {"type": "string"},
                "default": ["foo", "bar"],
                "minItems": 1,
                "maxItems": 3,
                "contains": {"type": "string"},
                "uniqueItems": True,
            },
        ),
        (
            Array(
                [String(), Integer()],
                default=["foo", 1],
                minItems=2,
                additionalItems=False,
            ),
            {
                "type": "array",
                "items": [{"type": "string"}, {"type": "integer"}],
                "default": ["foo", 1],
                "minItems": 2,
                "additionalItems": False,
            },
        ),
    ],
)
def test_array_serialize(element: Element, expected: Dict[str, Any]):
    assert element.serialize() == expected
