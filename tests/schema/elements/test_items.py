import pytest

from statham.schema.elements import Element, Integer, Nothing, String
from statham.schema.elements.items import Items


@pytest.mark.parametrize(
    "additional,expected",
    [
        (True, ""),
        (Element(), ""),
        (False, ", additionalItems=False"),
        (Nothing(), ", additionalItems=False"),
        (Integer(), ", additionalItems=Integer()"),
    ],
)
def test_properties_repr(additional, expected):
    properties = Items(String(), additional=additional)
    assert repr(properties) == ("Items(String()" + f"{expected})")
