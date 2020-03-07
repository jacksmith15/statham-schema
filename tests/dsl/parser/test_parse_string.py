import pytest

from statham.dsl.constants import NotPassed
from statham.dsl.elements import String
from statham.dsl.parser import parse


class TestParseString:
    @staticmethod
    @pytest.mark.parametrize(
        "schema",
        [{"type": "string"}, {"type": "string", "other_property": "value"}],
    )
    def test_with_no_args(schema):
        element = parse(schema)
        assert isinstance(element, String)
        assert element.default == NotPassed()
        assert element.format == NotPassed()
        assert element.pattern == NotPassed()
        assert element.minLength == NotPassed()
        assert element.maxLength == NotPassed()
        assert repr(element) == "String()"

    @staticmethod
    def test_with_full_args():
        schema = {
            "type": "string",
            "default": "foobar",
            "format": "my_format",
            "pattern": ".*",
            "minLength": 3,
            "maxLength": 5,
        }

        element = parse(schema)
        assert isinstance(element, String)
        assert element.default == "foobar"
        assert element.format == "my_format"
        assert element.pattern == ".*"
        assert element.minLength == 3
        assert element.maxLength == 5
        assert repr(element) == (
            """String(default='foobar', format='my_format', pattern='.*', minLength=3, maxLength=5)"""
        )
