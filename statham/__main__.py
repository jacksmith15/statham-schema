from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from logging import getLogger, INFO
from os import path
from typing import Any, Dict, Iterator, TextIO, Tuple
from sys import argv, stdout

from statham.dependency_resolver import ClassDependencyResolver
from statham.models import parse_schema
from statham.parser import get_schema
from statham.serializer import serialize_object_schemas


LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)


@contextmanager
def parse_args(args) -> Iterator[Tuple[Namespace, TextIO]]:
    parser = ArgumentParser(
        description="Generate python attrs models from JSONSchema files."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Specify path to top-level schema document.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=(
            "Output directory or file to write the output to. If this "
            "is a directory, the command will derive the name from the "
            "input file. If not passed, the command will write to "
            "stdout."
        ),
    )
    parsed = parser.parse_args(args)
    if parsed.output:
        if path.isdir(parsed.output):
            filename = ".".join(path.basename(parsed.input).split(".")[:-1])
            output_path = path.join(parsed.output, ".".join([filename, "py"]))
        else:
            output_path = parsed.output
        with open(output_path, "w", encoding="utf8") as file:
            yield parsed, file
        return
    yield parsed, stdout
    return


def convert_schema(schema_dict: Dict[str, Any]) -> str:
    return serialize_object_schemas(
        ClassDependencyResolver(parse_schema(schema_dict))
    )


def main(input_file: str) -> str:
    schema = get_schema(input_file)
    return convert_schema(schema)


if __name__ == "__main__":
    with parse_args(argv[1:]) as (args, output):
        output.write(main(args.input))
