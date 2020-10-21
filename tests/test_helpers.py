import pytest

from statham.schema.parser import _title_format


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
        ("FooBar!", "FooBar"),
        ("Foo Bar!", "FooBar"),
        ("Foo+bar", "FooBar"),
        ("Foo+-bar", "FooBar"),
        ("+Foo-bar", "FooBar"),
        ("Foo,bar", "FooBar"),
    ],
)
def test_title_format_produces_expected_output(title: str, expected: str):
    actual = _title_format(title)
    assert (
        actual == expected
    ), f"Expected '{title}' --> '{expected}', got '{actual}'"
