from argparse import ArgumentParser, RawTextHelpFormatter
from contextlib import contextmanager
from logging import getLogger, INFO
from os import path
from typing import Iterator, TextIO, Tuple
from sys import argv, stdout

from json_ref_dict import materialize, RefDict

from statham.dsl.parser import parse
from statham.serializer import serialize_python
from statham.titles import title_labeller


# TODO: Write tests for references via keys containing /.


LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)


def parse_input_arg(input_arg: str) -> str:
    """Parse input URI as a valid JSONSchema ref.

    This tool accepts bare base URIs, without the JSON Pointer,
    so these should be converted to a root pointer.
    """
    if "#" not in input_arg:
        return input_arg + "#/"
    return input_arg


@contextmanager
def parse_args(args) -> Iterator[Tuple[str, TextIO]]:
    """Parse arguments, abstracting IO in a context manager."""

    parser = ArgumentParser(
        description="Generate statham DSL models from JSONSchema files.",
        formatter_class=RawTextHelpFormatter,
        add_help=False,
    )
    required = parser.add_argument_group("Required arguments")
    required.add_argument(
        "--input",
        type=str,
        required=True,
        help="""Specify the path to the JSON Schema to be generated.

If the target schema is not at the root of a document, specify the
JSON Pointer in the same format as a JSONSchema `$ref`, e.g.
`--input path/to/document.json#/definitions/schema`

""",
    )
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument(
        "--output",
        type=str,
        default=None,
        help="""Output directory or file in which to write the output.

If the provided path is a directory, the command will derive the name
from the input argument. If not passed, the command will write to
stdout.

""",
    )
    optional.add_argument(
        "-h",
        "--help",
        action="help",
        help="Display this help message and exit.",
    )
    parsed = parser.parse_args(args)
    input_arg: str = parse_input_arg(parsed.input)
    if parsed.output:
        if path.isdir(parsed.output):
            filename = ".".join(path.basename(parsed.input).split(".")[:-1])
            output_path = path.join(parsed.output, ".".join([filename, "py"]))
        else:
            output_path = parsed.output
        with open(output_path, "w", encoding="utf8") as file:
            yield input_arg, file
        return
    yield input_arg, stdout
    return


def main(input_uri: str) -> str:
    """Get the schema, and then return the generated python module.

    Example:
    ```
    main("https://json-schema.org/draft-04/schema#/")
    ```

    :param input_uri: This must follow the conventions of a JSONSchema
        '$ref' attribute.
    :return: Python module contents for generated models, as a string.
    """
    schema = materialize(RefDict(input_uri), context_labeller=title_labeller())
    return serialize_python(*parse(schema))


def entry_point():
    """Entry point for command.

    Parse arguments, read from input and write to output.
    """
    with parse_args(argv[1:]) as (uri, output):  # pragma: no cover
        output.write(main(uri))  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    entry_point()  # pragma: no cover
