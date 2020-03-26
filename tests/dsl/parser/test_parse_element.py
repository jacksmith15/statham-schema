import pytest

from statham.dsl.elements import Element
from statham.dsl.exceptions import SchemaParseError
from statham.dsl.parser import parse_element


def test_parsing_empty_schema_results_in_base_element():
    assert type(parse_element({})) is Element


def test_parsing_schema_with_unknown_fields_ignores_them():
    assert type(parse_element({"foo": "bar"})) is Element


def test_parsing_schema_with_bad_type_raises():
    with pytest.raises(SchemaParseError):
        parse_element({"type": {}})
