from typing import Dict, Mapping

import pytest

from statham.constants import JSONElement
from statham.models import ObjectSchema


@pytest.fixture()
def valid_schema() -> Dict[str, JSONElement]:
    return {
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


@pytest.fixture
def schema_model(valid_schema: Mapping[str, JSONElement]) -> ObjectSchema:
    return ObjectSchema(**valid_schema)
