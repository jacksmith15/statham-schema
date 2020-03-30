import pytest

from statham.dsl.constants import UNSUPPORTED_SCHEMA_KEYWORDS
from statham.dsl.elements import Element, Nothing, String
from statham.dsl.property import Property
from statham.dsl.exceptions import FeatureNotImplementedError, SchemaParseError
from statham.dsl.parser import parse_element


def test_parsing_empty_schema_results_in_base_element():
    assert parse_element({}) == Element()


def test_parsing_schema_with_unknown_fields_ignores_them():
    assert parse_element({"foo": "bar"}) == Element()


def test_parsing_boolean_schema_true_gives_base_element():
    assert parse_element(True) == Element()


def test_parsing_boolean_schema_false_gives_nothing():
    assert parse_element(False) == Nothing()


@pytest.mark.xfail(raises=FeatureNotImplementedError)
@pytest.mark.parametrize("keyword", UNSUPPORTED_SCHEMA_KEYWORDS)
def test_parsing_unsupported_keywords(keyword):
    assert parse_element({keyword: True})


def test_parsing_schema_with_bad_type_raises():
    with pytest.raises(SchemaParseError):
        parse_element({"type": {}})


def test_parse_element_with_arguments():
    schema = {
        "default": "foo",
        "minItems": 3,
        "maxItems": 5,
        "minimum": 3,
        "maximum": 5,
        "minLength": 3,
        "maxLength": 5,
        "required": ["value"],
        "properties": {"value": {"type": "string"}},
        "additionalProperties": {"type": "string"},
        "items": {"type": "string"},
    }
    expected = Element(
        default="foo",
        minItems=3,
        maxItems=5,
        minimum=3,
        maximum=5,
        minLength=3,
        maxLength=5,
        required=["value"],
        properties={"value": Property(String(), required=True)},
        additionalProperties=String(),
        items=String(),
    )
    assert parse_element(schema) == expected
