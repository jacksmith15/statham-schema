from black import assert_equivalent as assert_ast_equal

from jsonschema_objects.__main__ import main


def test_that_main_produces_expected_output():
    """Test that the output is equivalent to generated models.

    To avoid reinventing the wheel, this borrows from black`s ast
    comparison tool. To attempt to avoid misleading errors, it cuts
    out black's message (which is very specific). If black's error
    reporting changes this may need to be updated.
    """
    generated = main("tests/jsonschemas/simple.json")
    with open("tests/models/simple.py") as file:
        expected = file.read()
    try:
        assert_ast_equal(expected, generated)
    except AssertionError as exc:
        raise AssertionError(
            "Generated code differed from expected. The following diff "
            f"might be helpful: {str(exc).split('helpful:')[-1]}"
        ) from None
