import pytest

from statham.constants import get_flag, NOT_PROVIDED


@pytest.mark.parametrize("args", [tuple(), ("foo")])
def test_get_flat_fails_with_bad_args(args):
    with pytest.raises(ValueError):
        _ = get_flag(*args)


def test_not_provided_repr():
    assert repr(NOT_PROVIDED) == "<NOTPROVIDED>"
