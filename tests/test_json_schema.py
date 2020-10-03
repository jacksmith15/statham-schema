from io import StringIO
import json
import os
from os import path
from typing import Any, Dict, Iterator, List, NamedTuple, Optional
from unittest.mock import patch
from urllib.request import urlopen

from json_ref_dict import materialize, RefDict
from json_ref_dict.loader import get_document
from json_ref_dict.ref_pointer import resolve_uri
import pytest

from statham.schema.parser import parse_element
from statham.schema.exceptions import (
    FeatureNotImplementedError,
    ValidationError,
)
from statham.titles import title_labeller
from tests.helpers import no_raise


NOT_IMPLEMENTED = (
    "optional",
    # "refRemote",
    # The following are not yet supported.
    "Location-independent identifier",
    "Location-independent identifier with absolute URI",
    "Location-independent identifier with base URI change in subschema",
    "root ref in remote ref",
    "base URI change - change folder in subschema",
    "base URI change - change folder",
    "base URI change",
    # The following is not supported.
    "Recursive references between schemas",
    # The following is indirectly not supported.
    "definitions",
    # The following have $ref into themselves - which creates a cycle unless
    #  a $ref does not override other members (which it should
    #  according to the spec!)
    "$ref to boolean schema true",
    "$ref to boolean schema false",
    "nested refs",
)


def _add_titles(schema):
    if not isinstance(schema, (dict, list)):
        return schema
    if isinstance(schema, list):
        return [_add_titles(val) for val in schema]
    return {
        "title": "Title",
        **{key: _add_titles(value) for key, value in schema.items()},
    }


def iter_files(filepath: str):
    if path.isdir(filepath):
        for subpath in os.listdir(filepath):
            yield from iter_files(path.join(filepath, subpath))
    else:
        yield filepath, load_file(filepath)


def load_file(filepath: str) -> Optional[List]:
    with open(filepath, "r", encoding="utf8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return None


DIRECTORY = "tests/JSON-Schema-Test-Suite/tests"
SUPPORTED_DRAFTS = ("draft6",)


class Param(NamedTuple):
    draft: str
    feature: str
    case: str
    test: str
    schema: Dict
    data: Any
    valid: bool

    def __str__(self):
        return f"{self.draft} | {self.feature} | {self.case} | {self.test}"

    @property
    def implemented(self):
        for tag in NOT_IMPLEMENTED:
            if tag in str(self):
                return False
        return True

    @property
    def marks(self):
        return [
            pytest.mark.skipif(not self.implemented, reason="Not implemented")
        ]


def _extract_tests(directory: str) -> Iterator[Param]:
    draft_dir = lambda _: path.join(directory, _)
    draft_tests = (
        (
            draft,
            (
                (key.replace(draft_dir(draft), "").lstrip("/"), value)
                for key, value in iter_files(draft_dir(draft))
                if value
            ),
        )
        for draft in SUPPORTED_DRAFTS
    )
    feature_tests = (
        (key.replace(directory, ""), value)
        for key, value in iter_files(directory)
        if value
    )
    for draft, feature_tests in draft_tests:
        for name, feature_test in feature_tests:
            for test_case in feature_test:
                for test in test_case["tests"]:
                    assert isinstance(test, dict)
                    param = Param(
                        draft=draft,
                        feature=name,
                        case=test_case["description"],
                        test=test["description"],
                        schema=test_case["schema"],
                        data=test["data"],
                        valid=test["valid"],
                    )
                    yield pytest.param(param, marks=param.marks)


@pytest.mark.parametrize("param", _extract_tests(DIRECTORY), ids=str)
def test_jsonschema_official_test(param: Param):
    schema = _load_schema(param.schema)
    try:
        element = parse_element(schema)
    except FeatureNotImplementedError:
        return
    with no_raise() if param.valid else pytest.raises(
        (TypeError, ValidationError)
    ):
        _ = element(param.data)


def _load_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Mock the RefDict loader.

    De-references and labels schema.
    """

    def _mock_url_open(uri):
        if "testuri.json" in uri:
            conn = StringIO()
            json.dump(schema, conn)
            conn.seek(0)
            conn.url = uri
            return conn
        base_uri = "file://" + path.join(
            os.getcwd(), "tests/JSON-Schema-Test-Suite/remotes"
        )
        uri = uri.replace("http://localhost:1234", base_uri)
        return urlopen(uri)

    with patch("json_ref_dict.loader.urlopen", new=_mock_url_open):
        resolve_uri.cache_clear()
        get_document.cache_clear()
        ref_dict = RefDict.from_uri("testuri.json#/")
        return materialize(ref_dict, context_labeller=title_labeller())


def test_load_schema():
    with open(
        path.join(DIRECTORY, "draft6", "items.json"), "r", encoding="utf8"
    ) as file:
        data = json.load(file)
    schema = next(
        item for item in data if item["description"] == "items and subitems"
    )["schema"]
    sub_item = {
        "type": "object",
        "required": ["foo"],
        "_x_autotitle": "sub-item",
    }
    item = {
        "type": "array",
        "additionalItems": False,
        "items": [sub_item, sub_item],
        "_x_autotitle": "item",
    }
    expected = {
        "type": "array",
        "additionalItems": False,
        "items": [item, item, item],
        "definitions": {
            "item": item,
            "sub-item": sub_item,
            "_x_autotitle": "definitions",
        },
        "_x_autotitle": "testuri",
    }
    loaded_schema = _load_schema(schema)
    assert loaded_schema == expected
