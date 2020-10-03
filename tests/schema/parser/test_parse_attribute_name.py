import pytest

from statham.schema.parser import _parse_attribute_name


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "name"),
        ("default", "default"),
        ("properties", "properties"),
        ("options", "options"),
        ("additional_properties", "additional_properties"),
        ("_dict", "_dict_"),
        ("__init__", "__init___"),
        ("name with space", "name_with_space"),
        ("lowerCamelCase", "lowerCamelCase"),
        ("name_with_number_6", "name_with_number_6"),
        ("6_leading_number", "_6_leading_number"),
        ("name_with_$", "name_with_dollar_sign"),
        ("", "blank"),
        ("+", "plus_sign"),
        ("$ref", "dollar_sign_ref"),
        ("ref$", "ref_dollar_sign"),
        ("ref$ref", "ref_dollar_sign_ref"),
    ],
)
def test_parse_attribute_name(name: str, expected: str):
    assert _parse_attribute_name(name) == expected
