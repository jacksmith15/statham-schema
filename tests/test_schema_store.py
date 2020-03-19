from http import HTTPStatus
import operator as op
import os
import pytest

import requests

from statham.__main__ import main
from tests.helpers import no_raise


# This is a magic pytest constant.
# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.skipif(
        os.getenv("INTEGRATION", "false").lower() not in ("true", "1"),
        reason=(
            "This is for aiding integration with schemas that are "
            "partially compliant. We iterate over sample schemas "
            "hosted on 'schemastore.org' and attempt to generate code "
            "for them."
        ),
    )
]


_CATALOG_URI = "http://schemastore.org/api/json/catalog.json"
_IGNORED_SCHEMAS = ("Ansible", "Opctl")  # Way too big.  # Bad ref encoding.


def iter_schemas():
    response = requests.get(_CATALOG_URI)
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    for schema in body["schemas"]:
        if schema["name"] not in _IGNORED_SCHEMAS:
            yield schema


@pytest.mark.parametrize(
    "schema_ref", iter_schemas(), ids=op.itemgetter("name")
)
def test_parsing_external_jsonschema(schema_ref):
    url = schema_ref["url"]
    with no_raise():
        _ = main(url)
