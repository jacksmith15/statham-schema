from collections import UserDict
from functools import lru_cache, partial
from os import path
from typing import Any, Dict, Optional

import yaml

from statham.constants import JSONElement, IGNORED_SCHEMA_KEYWORDS
from statham.exceptions import NotImplementedSchemaParserError, SchemaParseError


# This is provided in the standard library expressly for subclassing.
class Document(UserDict):  # pylint: disable=too-many-ancestors
    """Simple dict wrapper with helper for retrieving JSON"""

    @lru_cache(maxsize=None)
    def get_ref(self, reference_path: str) -> Dict[str, Any]:
        """Simple path getter for the dictionary.

        :raises KeyError: if the path is not present in the dictionary.
        """
        output = dict(self)
        for breadcrumb in reference_path.strip("/").split("/"):
            output = self[breadcrumb]
        return output


class FileRefLoader:

    base_uri: str

    def __init__(self, base_uri: str):
        self.base_uri = base_uri

    def __repr__(self):
        return f"{type(self).__name__}({self.base_uri})"

    def load_schema(self):
        schema: Document = self._document()
        return self._dereference(schema)

    @lru_cache(maxsize=None)
    def get_ref(self, reference: str) -> Dict[str, Any]:
        filename, reference_path = reference.split("#")
        try:
            return self._document(filename).get_ref(reference_path)
        except KeyError:
            raise SchemaParseError.unresolvable_pointer(reference)

    @lru_cache(maxsize=None)
    def _document(self, uri: str = None) -> Document:
        uri = uri or path.basename(self.base_uri)
        filename = path.join(path.dirname(self.base_uri), uri)
        if not filename.endswith((".json", ".yaml", ".yml")):
            raise TypeError(f"File {filename} has unsupported extension.")
        with open(filename, "r", encoding="utf8") as file:
            content = file.read()
        return Document(yaml.safe_load(content))

    def _dereference(self, element: Any) -> Any:
        if isinstance(element, list):
            return [self._dereference(item) for item in element]
        if not isinstance(element, dict):
            return element
        reference = element.get("$ref")
        if reference:
            ref_schema = self.get_ref(reference)
            if not isinstance(ref_schema, dict):
                raise NotImplementedSchemaParserError.non_object_refs()
            ref_schema["title"] = reference.split("/")[-1]
        return {key: self._dereference(value) for key, value in element.items()}


def get_ref(
    schema: Dict[str, Any], base_uri: Optional[str], reference: str
) -> Dict[str, Any]:
    filename, path = reference.split("#")
    if filename:
        assert base_uri, "Cannot resolve remote refs without base_uri."
        raise NotImplementedSchemaParserError.remote_refs()
    output = schema
    for breadcrumb in path.strip("/").split("/"):
        try:
            output = output[breadcrumb]
        except KeyError:
            raise SchemaParseError.unresolvable_pointer(reference)
    return output


def dereference_schema(
    schema: Dict[str, Any], base_uri: Optional[str], element: JSONElement
) -> JSONElement:
    deref = partial(dereference_schema, schema, base_uri)
    if isinstance(element, list):
        return [deref(item) for item in element]
    if not isinstance(element, dict):
        return element
    if "$ref" in element:
        ref_schema = get_ref(schema, base_uri, element["$ref"])
        if not isinstance(ref_schema, dict):
            raise NotImplementedSchemaParserError.non_object_refs()
        ref_schema["title"] = element["$ref"].split("/")[-1]
        return deref(ref_schema)
    return {
        key: deref(value)
        for key, value in element.items()
        if key not in IGNORED_SCHEMA_KEYWORDS
    }
