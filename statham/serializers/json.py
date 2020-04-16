import inspect
from typing import Any, Dict

from statham.dsl.elements import (
    Array,
    Boolean,
    CompositionElement,
    Element,
    Integer,
    Not,
    Nothing,
    Null,
    Number,
    String,
)
from statham.dsl.elements.meta import ObjectMeta
from statham.dsl.property import _Property
from statham.orderer import get_object_classes


# TODO: Could include definitions kwarg:
#   serialize_json(*element, definitions={"uuid": String(format="uuid")})
# and reference any elements which match.
def serialize_json(*elements: Element) -> Dict[str, Any]:
    """Serialize elements to a JSON Schema dictionary.

    Object classes are included in definitions. The first element is
    the top-level schema.
    """
    primary = elements[0]
    object_classes = get_object_classes(*elements)
    schema = {
        **serialize_element(primary, use_refs=True),
        "definitions": {
            object_class.__name__: serialize_element(
                object_class, use_refs=True
            )
            for object_class in object_classes
            if object_class is not primary
        },
    }
    if not schema["definitions"]:
        del schema["definitions"]
    return schema


def serialize_element(element: Element, use_refs: bool = False):
    """Convert a DSL to a JSON Schema dictionary.

    This does the heavy lifting behind `serialize_json`.
    """
    if isinstance(element, Nothing):
        return False
    schema = {
        param.name: getattr(element, param.name, param.default)
        for param in inspect.signature(Element.__init__).parameters.values()
        if param.kind == param.KEYWORD_ONLY
        and getattr(element, param.name, param.default) != param.default
    }
    if not schema.get("properties", True):
        del schema["properties"]
    if "properties" in schema:
        schema["required"] = [
            prop.source
            for prop in schema["properties"].values()
            if prop.required
        ]
    if not schema.get("required", True):
        del schema["required"]
    if isinstance(element, CompositionElement):
        schema[element.mode] = element.elements
    if isinstance(element, Not):
        schema["not"] = element.element
    if type(element) in _TYPE_MAPPING:  # pylint: disable=unidiomatic-typecheck
        schema["type"] = _TYPE_MAPPING[type(element)]
    if isinstance(element, ObjectMeta):
        schema["title"] = element.__name__
    return _serialize_recursive(schema, use_refs=use_refs)


_TYPE_MAPPING = {
    Array: "array",
    Boolean: "boolean",
    Integer: "integer",
    Null: "null",
    ObjectMeta: "object",
    Number: "number",
    String: "string",
}


def _serialize_recursive(data: Any, use_refs: bool = False) -> Any:
    """Recursively serialize DSL elements."""
    if isinstance(data, ObjectMeta) and use_refs:
        return {"$ref": f"#/definitions/{data.__name__}"}
    if isinstance(data, _Property):
        return _serialize_recursive(data.element, use_refs=use_refs)
    if isinstance(data, Element):
        return serialize_element(data, use_refs=use_refs)
    if not isinstance(data, (list, dict)):
        return data
    if isinstance(data, list):
        return [_serialize_recursive(item, use_refs=use_refs) for item in data]
    return {
        key: _serialize_recursive(value, use_refs=use_refs)
        for key, value in data.items()
    }
