from sys import stdout
from unittest.mock import patch, mock_open

import pytest

from statham.__main__ import parse_args, parse_input_arg


def test_arg_parser_stdout():
    with parse_args(["--input", "foo.py"]) as (input_uri, output):
        assert output == stdout
        assert input_uri == "foo.py#/"


@pytest.fixture()
def _mock_open_file():
    with patch("builtins.open", mock_open(read_data="data")) as _mock_open_file:
        yield _mock_open_file


@pytest.fixture(params=[True, False])
def _is_dir(request):
    with patch("os.path.isdir") as mock_is_dir:
        mock_is_dir.return_value = request.param
        yield


def test_arg_parser_output_dir(_mock_open_file, _is_dir):
    with parse_args(["--input", "foo.py", "--output", "bar"]) as (
        input_uri,
        output,
    ):
        assert input_uri == "foo.py#/"
        assert output.read() == "data"


@pytest.mark.parametrize("input_arg", ["foo.json", "foo.json#/"])
def test_input_argparse(input_arg: str):
    assert parse_input_arg(input_arg) == "foo.json#/"
