import pytest

from statham.dsl.parser import parse
from statham.rorderer import orderer


def test_rorderer_no_cycles():
    schema = {
        "type": "object",
        "title": "Parent",
        "required": ["category"],
        "properties": {
            "category": {
                "type": "object",
                "title": "Category",
                "properties": {"value": {"type": "string"}},
                "default": {"value": "none"},
            },
            "default": {"type": "string"},
        },
        "definitions": {
            "other": {
                "type": "object",
                "title": "Other",
                "properties": {"value": {"type": "integer"}},
            }
        },
    }
    elements = parse(schema)
    ordered = list(map(repr, orderer(*elements)))
    assert ordered == ["Category", "Parent", "Other"]


def test_rorderer_with_cycles():
    parent = {
        "type": "object",
        "title": "Parent",
        "properties": {"child": {"type": "array", "items": {}}},
    }
    child = {"type": "object", "title": "Child", "properties": {"parent": {}}}
    parent["properties"]["child"]["items"] = child
    child["properties"]["parent"] = parent
    schema = {
        "definitions": {
            "parent": parent,
            "child": child,
            "other": {
                "type": "object",
                "title": "Other",
                "properties": {"value": {"type": "integer"}},
            },
        }
    }
    elements = parse(schema)
    ordered = list(map(repr, orderer(*elements)))
    assert ordered[0] == "Other"
    assert set(ordered[1:]) == {"Parent", "Child"}
