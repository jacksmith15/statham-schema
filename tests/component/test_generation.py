from os import listdir, path

import pytest

from tests.helpers import assert_generated_models_match


SCHEMA_DIR = "tests/jsonschemas"


@pytest.mark.parametrize(
    "filename",
    [
        ".".join(fn.split(".")[:-1])
        for fn in listdir(SCHEMA_DIR)
        if not path.isdir(path.join(SCHEMA_DIR, fn))
    ],
)
def test_that_main_produces_expected_output(filename: str):
    assert_generated_models_match(filename)
