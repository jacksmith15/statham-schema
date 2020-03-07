from typing import Any, Dict, Type

import pytest

from statham.dsl.elements import Element
from statham.dsl.parser import parse


class ParseSchemaCase:

    _SCHEMA: Dict[str, Any]
    _ELEMENT_TYPE: Type[Element]
    _ATTR_MAP: Dict[str, Any]
    _REPR: str

    @pytest.fixture(scope="class")
    def element(self):
        return parse(self._SCHEMA)

    def test_it_has_the_correct_type(self, element):
        assert isinstance(element, self._ELEMENT_TYPE)

    def test_its_keywords_are_set_correctly(self, element):
        for keyword, value in self._ATTR_MAP.items():
            assert getattr(element, keyword) == value

    def test_it_has_the_correct_repr(self, element):
        assert repr(element) == self._REPR
