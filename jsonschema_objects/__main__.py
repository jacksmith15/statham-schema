from argparse import ArgumentParser, Namespace
from logging import getLogger, INFO
from typing import Any, Dict

import yaml

from jsonschema_objects.dependency_resolver import ClassDependencyResolver
from jsonschema_objects.models import parse_schema
from jsonschema_objects.parser import dereference_schema
from jsonschema_objects.serializer import serialize_object_schemas


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
    return parser.parse_args()


def _load_schema(path: str) -> Dict[str, Any]:
    if not path.endswith((".json", ".yaml", ".yml")):
        raise TypeError(f"File {path} has unsupported extension.")
    with open(path, "r", encoding="utf8") as file:
        content = file.read()
    return yaml.safe_load(content)


def main(args: Namespace) -> None:
    schema = _load_schema(args.input)
    schema: Dict[str, Any] = parse_schema(
        dereference_schema(schema, f"file://{args.input}", schema)
    )
    class_schemas = ClassDependencyResolver(schema)
    serialized = serialize_object_schemas(class_schemas)
    print(serialized)


if __name__ == "__main__":
    main(parse_args())
