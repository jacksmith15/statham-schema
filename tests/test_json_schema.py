# TODO: Integrate with JSON Schema official test suite.
import json
import os
from os import path
from typing import Any, Dict, Iterator, List, NamedTuple, Optional

import pytest

from statham.dsl.parser import parse_element
from statham.dsl.exceptions import FeatureNotImplementedError, ValidationError
from tests.helpers import no_raise

# This is a magic pytest constant.
# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.skipif(
        os.getenv("OFFICIAL_TEST_SUITE", "false").lower() not in ("true", "1"),
        reason=("Test against JSONSchema official test pack."),
    )
]


NOT_IMPLEMENTED = (
    "optional",
    "additionalItems",
    "anchor",
    "const",
    "contains",
    "defs",
    "dependentRequired",
    "dependentSchemas",
    "dependencies",
    "enum",
    "if-then-else",
    "maxProperties",
    "minProperties",
    "not",
    "patternProperties",
    "propertyNames",
    "ref",
    "refRemote",
    "unevaluatedItems",
    "unevaluatedProperties",
    "uniqueItems",
)


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
    schema = {**param.schema, "title": "Test"}
    try:
        element = parse_element(schema)
    except FeatureNotImplementedError:
        return
    with no_raise() if param.valid else pytest.raises(
        (TypeError, ValidationError)
    ):
        _ = element(param.data)
