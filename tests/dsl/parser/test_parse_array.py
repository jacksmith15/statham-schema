import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Array, String
from statham.dsl.parser import parse


class TestParseArray:
    @staticmethod
    def test_with_no_items():
        with pytest.raises(TypeError):
            _ = parse({"type": "array"})

    @staticmethod
    def test_with_just_items():
        schema = {"type": "array", "items": {"type": "string"}}
        element = parse(schema)
        assert isinstance(element, Array)
        assert element.default == NotPassed()
        assert element.minItems == NotPassed()
        assert element.maxItems == NotPassed()
        assert isinstance(element.items, String)
        assert repr(element) == "Array(String())"

    @staticmethod
    def test_with_full_args():
        schema = {
            "type": "array",
            "items": {"type": "string"},
            "default": ["foo", "bar"],
            "minItems": 1,
            "maxItems": 3,
        }
        element = parse(schema)
        assert isinstance(element, Array)
        assert element.default == ["foo", "bar"]
        assert element.minItems == 1
        assert element.maxItems == 3
        assert isinstance(element.items, String)
        assert repr(element) == (
            """Array(String(), default=['foo', 'bar'], minItems=1, maxItems=3)"""
        )
