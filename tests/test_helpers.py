import pytest

from statham.constants import get_flag, NOT_PROVIDED
from statham.helpers import _title_format


@pytest.mark.parametrize("args", [tuple(), ("foo")])
def test_get_flat_fails_with_bad_args(args):
    with pytest.raises(ValueError):
        _ = get_flag(*args)


def test_not_provided_repr():
    assert repr(NOT_PROVIDED) == "<NOTPROVIDED>"


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Foo", "Foo"),
        ("foo", "Foo"),
        ("FooBar", "FooBar"),
        ("fooBar", "FooBar"),
        ("foo_bar", "FooBar"),
        ("foo_Bar", "FooBar"),
        ("Foo_Bar", "FooBar"),
        ("Foo_bar", "FooBar"),
        ("FooBarBaz", "FooBarBaz"),
        ("Foo_barBaz", "FooBarBaz"),
        ("foo_barBaz", "FooBarBaz"),
        ("foo bar Baz", "FooBarBaz"),
        ("foo_BARBaz", "FooBARBaz"),
        ("FooBar1", "FooBar1"),
        ("Foo1Bar", "Foo1Bar"),
        ("Foo1bar", "Foo1Bar"),
        ("foo1Bar", "Foo1Bar"),
        ("Foo-Bar", "FooBar"),
        ("foo-Bar", "FooBar"),
        ("Foo-bar", "FooBar"),
    ],
)
def test_title_format_produces_expected_output(title: str, expected: str):
    actual = _title_format(title)
    assert (
        actual == expected
    ), f"Expected '{title}' --> '{expected}', got '{actual}'"
