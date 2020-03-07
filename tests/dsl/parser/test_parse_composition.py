from typing import Any, Dict, List, Type

import pytest

from statham.dsl.elements import AnyOf, Array, Element, OneOf, String
from statham.dsl.parser import parse
from tests.dsl.parser.base import ParseSchemaCase


@pytest.mark.parametrize("keyword", ["anyOf", "oneOf"])
def test_parse_composition_fails_with_empty_list(keyword):
    schema = {keyword: []}
    with pytest.raises(TypeError):
        _ = parse(schema)


class ParseCompositionCase(ParseSchemaCase):
    _ATTR_MAP: Dict[str, Any] = {}
    _TYPE_MAP: List[Type[Element]]

    def test_it_has_the_correct_number_of_elements(self, element):
        assert len(element.elements) == len(self._TYPE_MAP)

    def test_the_elements_have_the_correct_type(self, element):
        assert [type(elem) for elem in element.elements] == self._TYPE_MAP


class TestParseAnyOfWithOneOption(ParseCompositionCase):
    _SCHEMA = {"anyOf": [{"type": "string"}]}
    _ELEMENT_TYPE = AnyOf
    _REPR = "AnyOf(String())"
    _TYPE_MAP: List[Type[Element]] = [String]


class TestParseAnyOfWithMultiOption(ParseCompositionCase):
    _SCHEMA = {
        "anyOf": [
            {"type": "string"},
            {"type": "array", "items": {"type": "string"}},
        ]
    }
    _ELEMENT_TYPE = AnyOf
    _REPR = "AnyOf(String(), Array(String()))"
    _TYPE_MAP = [String, Array]


class TestParseMultiTypeToAnyOf(ParseCompositionCase):
    _SCHEMA = {
        "type": ["string", "array"],
        "minLength": 3,
        "minItems": 3,
        "items": {"type": "string", "maxLength": 1},
    }
    _ELEMENT_TYPE = AnyOf
    _REPR = "AnyOf(String(minLength=3), Array(String(maxLength=1), minItems=3))"
    _TYPE_MAP = [String, Array]


class TestParseOneOfWithOneOption(ParseCompositionCase):
    _SCHEMA = {"oneOf": [{"type": "string"}]}
    _ELEMENT_TYPE = OneOf
    _REPR = "OneOf(String())"
    _TYPE_MAP: List[Type[Element]] = [String]


class TestParseOneOfWithMultiOption(ParseCompositionCase):
    _SCHEMA = {
        "oneOf": [
            {"type": "string"},
            {"type": "array", "items": {"type": "string"}},
        ]
    }
    _ELEMENT_TYPE = OneOf
    _REPR = "OneOf(String(), Array(String()))"
    _TYPE_MAP = [String, Array]
