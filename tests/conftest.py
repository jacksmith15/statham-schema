from typing import Dict, Mapping

import pytest

from statham.constants import JSONElement
from statham.models import ObjectSchema
from statham.titles import title_labeller


MAKE_LABEL = title_labeller()


def label_schema(schema, pointer="base.json#"):
    """Add titles to the schemas recursively.

    This is normally performed by `json_ref_dict.materialize`, but it is
    useful to be able to do this to ordinary dictionaries for unit
    testing.
    """
    if not isinstance(schema, (dict, list)):
        return schema
    if isinstance(schema, list):
        return [
            label_schema(item, pointer=pointer + f"/{idx}")
            for idx, item in enumerate(schema)
        ]
    return {
        **dict([MAKE_LABEL(pointer)]),
        **{
            key: label_schema(item, pointer=pointer + f"/{key}")
            for key, item in schema.items()
        },
    }


@pytest.fixture(scope="session")
def valid_schema() -> Dict[str, JSONElement]:
    schema = {
        "title": "Parent",
        "type": "object",
        "properties": {
            "related": {
                "title": "Related item",
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "integer", "multipleOf": 2},
                },
            },
            "children": {
                "type": "array",
                "items": {
                    "title": "Child item",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "proportion": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "maximum": 1,
                        },
                    },
                },
            },
            "name": {"type": "string"},
            "aliases": {"type": "array", "items": {"type": "string"}},
            "optional": {"type": ["null", "string"]},
        },
    }
    return label_schema(schema)


@pytest.fixture()
def schema_model(valid_schema: Mapping[str, JSONElement]) -> ObjectSchema:
    return ObjectSchema(**valid_schema)
