from black import assert_equivalent as assert_ast_equal

from jsonschema_objects.__main__ import main


def test_that_main_produces_expected_output():
    generated = main("tests/jsonschemas/simple.json")
    with open("tests/models/simple.py") as file:
        expected = file.read()
    try:
        assert_ast_equal(expected, generated)
    except AssertionError as exc:
        assert False, (
            "Generated code differed from expected.\n"
            f"{str(exc).split('helpful:')[-1]}"
        )
