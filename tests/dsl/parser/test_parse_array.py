import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import Array, String
from statham.dsl.parser import parse
from tests.dsl.parser.base import ParseSchemaCase


def test_parse_array_fails_with_no_items():
    with pytest.raises(TypeError):
        _ = parse({"type": "array"})


class TestParseArrayWithItems(ParseSchemaCase):
    _SCHEMA = {"type": "array", "items": {"type": "string"}}
    _ELEMENT_TYPE = Array
    _ATTR_MAP = {
        "default": NotPassed(),
        "minItems": NotPassed(),
        "maxItems": NotPassed(),
    }
    _REPR = "Array(String())"

    def test_its_items_has_the_correct_type(self, element):
        assert isinstance(element.items, String)


class TestParseArrayWithFullKeywords(ParseSchemaCase):

    _SCHEMA = {
        "type": "array",
        "items": {"type": "string"},
        "default": ["foo", "bar"],
        "minItems": 1,
        "maxItems": 3,
    }
    _ELEMENT_TYPE = Array
    _ATTR_MAP = {"default": ["foo", "bar"], "minItems": 1, "maxItems": 3}
    _REPR = "Array(String(), default=['foo', 'bar'], minItems=1, maxItems=3)"

    def test_its_items_has_the_correct_type(self, element):
        assert isinstance(element.items, String)
