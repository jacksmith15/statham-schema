from functools import partial
from typing import Any, Dict, Optional

from jsonschema_objects.constants import IGNORED_SCHEMA_KEYWORDS


def get_ref(
    schema: Dict[str, Any], base_uri: Optional[str], reference: str
) -> Dict[str, Any]:
    filename, path = reference.split("#")
    if filename:
        assert base_uri
        raise NotImplementedError
    output = schema
    for breadcrumb in path.strip("/").split("/"):
        try:
            output = output[breadcrumb]
        except KeyError:
            raise KeyError(f"Couldnt resolve pointer: {reference}")
    return output


def dereference_schema(
    schema: Dict[str, Any], base_uri: Optional[str], element: Any
) -> Dict[str, Any]:
    deref = partial(dereference_schema, schema, base_uri)
    if isinstance(element, list):
        return [deref(item) for item in element]
    if not isinstance(element, dict):
        return element
    if "$ref" in element:
        ref_schema = get_ref(schema, base_uri, element["$ref"])
        if not isinstance(ref_schema, dict):
            raise NotImplementedError("Only support refs to objects.")
        ref_schema["title"] = element["$ref"].split("/")[-1]
        return deref(ref_schema)
    return {
        key: deref(value)
        for key, value in element.items()
        if key not in IGNORED_SCHEMA_KEYWORDS
    }
