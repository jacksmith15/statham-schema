from contextlib import contextmanager
from typing import Dict, Optional, Tuple, Type, Union

from black import assert_equivalent as assert_ast_equal
import pytest

from statham.__main__ import main


def assert_generated_models_match(filename: str) -> None:
    """Test that the output is equivalent to generated models.

    To avoid reinventing the wheel, this borrows from black`s ast
    comparison tool. To attempt to avoid misleading errors, it cuts
    out black's message (which is very specific). If black's error
    reporting changes this may need to be updated.
    """
    generated = main(f"tests/jsonschemas/{filename}.json#/")
    with open(f"tests/models/{filename}.py") as file:
        expected = file.read()
    try:
        assert_ast_equal(expected, generated)
    except AssertionError as exc:
        raise AssertionError(
            "Generated code differed from expected. The following diff "
            f"might be helpful: {str(exc).split('helpful:')[-1]}"
        ) from None


def abstract_model_instantiate_test(
    model: Type,
    kwargs: Dict,
    exception_type: Optional[Type[Exception]],
    exception_msg: Optional[str],
):
    if not exception_type:
        try:
            assert model(kwargs)
        except Exception as exc:
            raise AssertionError(f"Failed field validation: {kwargs}") from exc
        return
    with pytest.raises(Exception) as excinfo:
        model(kwargs)
    assert excinfo.type is exception_type, (
        f"Raised incorrect exception type. Expected {exception_type}, "
        f"got {excinfo.type}. kwargs: {kwargs}"
    )
    actual_msg = str(excinfo.value)
    assert (exception_msg or "") in actual_msg, (
        f"Unexpected error message: '{actual_msg}'. Expected to contain "
        f"'{exception_msg}'."
    )


@contextmanager
def no_raise(*exception_types: Type[Exception]):
    """Simply assert that a given code block does nto raise.

    Essentially the inverse of `pytest.raises`.

    :param exception_types: The type of exceptions to fail on. Does
        not implement handling on other exceptions - these will raise
        normally.
    """
    types: Union[
        Type[Exception], Tuple[Type[Exception], ...]
    ] = exception_types or Exception
    try:
        yield
    except types as exc:  # pylint: disable=broad-except
        assert False, str(exc)
