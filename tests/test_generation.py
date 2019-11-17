import os

import pytest

from tests.helpers import assert_generated_models_match


@pytest.mark.parametrize(
    "filename",
    [".".join(fn.split(".")[:-1]) for fn in os.listdir("tests/jsonschemas")],
)
def test_that_main_produces_expected_output(filename: str):
    assert_generated_models_match(filename)
