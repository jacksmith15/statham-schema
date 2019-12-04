from functools import lru_cache
from os import path
from typing import Any, Dict, List, TypeVar

from jsonpointer import JsonPointer
import yaml

from statham.constants import IGNORED_SCHEMA_KEYWORDS
from statham.exceptions import NotImplementedSchemaParserError


T = TypeVar("T", List, Dict, Any)


class BaseURI:
    """Base URI of a schema document.

    Used for computing relative references.
    """

    def __init__(self, base_uri: str):
        self.dir = path.dirname(base_uri)
        self.name = path.basename(base_uri)

    def relative(self, uri: str) -> "BaseURI":
        if not uri:
            return self
        return BaseURI(path.join(self.dir, uri))

    def __str__(self):
        return path.join(self.dir, self.name)


@lru_cache(maxsize=None)
def get_schema_document(uri: BaseURI):
    """Get a schema document from the file-system."""
    with open(str(uri), "r", encoding="utf8") as file:
        content = file.read()
    return yaml.safe_load(content)


def dereference(base_uri: BaseURI, data: T) -> T:
    """Recursively resource references in a schema document."""
    if isinstance(data, list):
        return [dereference(base_uri, subitem) for subitem in data]
    if not isinstance(data, dict):
        return data
    if "$ref" in data:
        uri, ref = data["$ref"].split("#")
        related_uri = base_uri.relative(uri)
        remote = dereference(
            related_uri,
            JsonPointer(ref).resolve(get_schema_document(related_uri)),
        )
        if not isinstance(remote, dict):
            raise NotImplementedSchemaParserError.non_object_refs()
        remote["title"] = ref.strip("/").split("/")[-1]
        return remote
    return {
        key: dereference(base_uri, value)
        for key, value in data.items()
        if key not in IGNORED_SCHEMA_KEYWORDS
    }


def get_schema(filename: str):
    """Load a complete dereferenced schema."""
    uri = BaseURI(filename)
    return dereference(uri, get_schema_document(uri))
