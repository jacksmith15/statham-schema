from argparse import ArgumentParser, Namespace
import json
from logging import getLogger, INFO
from os import listdir
from os.path import basename, join
from typing import Any, Dict, Tuple

import yaml

from jsonschema_objects.parser import parse_schema
from jsonschema_objects.renderer import get_class_defs, to_python


LOGGER = getLogger(__name__)
LOGGER.setLevel(INFO)


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Batch download a set of tracks from slider.")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Specify path to top-level schema document.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Specify a folder in which to store the module schemas.",
    )
    return parser.parse_args()


def _load_schema(path: str) -> Dict[str, Any]:
    if not path.endswith((".json", ".yaml", ".yml")):
        raise TypeError(f"File {path} has unsupported extension.")
    with open(path, "r", encoding="utf8") as file:
        content = file.read()
    return yaml.safe_load(content)


def main(args: Namespace) -> None:
    schema: Dict[str, Any] = parse_schema(_load_schema(args.input), f"file://{args.input}")
    to_python(schema.items)
    class_defs = get_class_defs(schema.items)
    import ipdb;ipdb.set_trace()


if __name__ == "__main__":
    print(main(parse_args()))
