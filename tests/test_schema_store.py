from http import HTTPStatus
import operator as op
import os
import pytest

import requests

from statham.__main__ import main


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
_IGNORED_SCHEMAS = (
    "Ansible",  # Way too big.
    "httparchive",  # Too big.
    "lsdlschema.json",  # Too big.
    "Carafe",  # Too big.
    "Opctl",  # Bad ref encoding.
    ".angular-cli.json",  # Bad refs.
    "Avro Avsc",  # Cyclical deps.
    "bucklescript",  # Cyclical deps.
    "circleciconfig.json",  # Bad refs.
    ".cirrus.yml",  # Bad refs.
    "AWS CloudFormation",  # Bad refs.
    "AWS CloudFormation Serverless Application Model (SAM)",  # Bad refs.
    "dss-2.0.0.json",  # Bad ref encoding.
    "GitHub Workflow",  # Cyclical deps.
    "Jenkins X Pipelines",  # Cyclical deps.
    "Renovate",  # Cyclical deps.
    "sarif-1.0.0.json",  # Cyclical deps.
    "sarif-2.0.0.json",  # Cyclical deps.
    "Source Maps v3",  # Bad UTF encoding.
    "skyuxconfig.json",  # Not found.
    "batect.yml",  # Forbidden.
    "2.0.0-csd.2.beta.2018-10-10",  # Moved.
    "compilerconfig.json",  # Moved.
    "prometheus.rules.json",  # Moved.
    "fabric.mod.json",  # Moved.
    "neoload",  # Bad content type.
    "Briefcase",  # Bad content type.
    "component.json",  # Cyclical deps.
    "sarif-2.1.0-rtm.2",  # Cyclical deps.
    "sarif-external-property-file-2.1.0-rtm.2",  # Cyclical deps.
    "sarif-2.1.0-rtm.3",  # Cyclical deps.
    "sarif-external-property-file-2.1.0-rtm.3",  # Cyclical deps.
    "sarif-2.1.0-rtm.4",  # Cyclical deps.
    "sarif-external-property-file-2.1.0-rtm.4",  # Cyclical deps.
    "sarif-2.1.0-rtm.5",  # Cyclical deps.
    "sarif-external-property-file-2.1.0-rtm.5",  # Cyclical deps.
    "template.json",  # Cyclical deps.
    "tmLanguage",  # Cyclical deps.
    "vega-lite.json",  # Cyclical deps.
    "KSP-CKAN 1.26.4",  # Cyclical deps.
    "JSON Schema Draft 4",  # Cyclical deps.
)


def iter_schemas():
    response = requests.get(_CATALOG_URI)
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    for schema in body["schemas"]:
        if schema["name"] not in _IGNORED_SCHEMAS:
            yield schema


@pytest.fixture(scope="session")
def outfile():
    with open("integration-report.csv", "w") as file:
        yield file


@pytest.mark.parametrize(
    "schema_ref", iter_schemas(), ids=op.itemgetter("name")
)
def test_parsing_external_jsonschema(schema_ref, outfile):
    url = schema_ref["url"]
    try:
        _ = main(url)
    except Exception as exc:  # pylint: disable=broad-except
        outfile.write(f"{schema_ref['name']},{url},\"{str(exc)[:1000]}\"\n")
        assert False
