import inspect
from functools import partial
from typing import Any, Dict, Optional

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
from statham.serializers.orderer import get_object_classes


def serialize_json(
    *elements: Element, definitions: Dict[str, Element] = None
) -> Dict[str, Any]:
    """Serialize DSL elements to a JSON Schema dictionary.

    Object classes are included in definitions. The first element is
    the top-level schema.

    :param elements: The :class:`~statham.dsl.elements.Element` objects
        to serialize.
    :param definitions: A dictionary of elements which should be members
      of the schema definitions keyword, and referenced everywhere else.
    :return: A JSON-serializable dictionary containing the JSON Schema
        for the provided element(s).
    """
    primary = elements[0]
    object_classes = get_object_classes(*elements)
    serialize = partial(
        _serialize_element, object_refs=True, definitions=definitions
    )
    schema: Dict[str, Any] = {
        **serialize(primary),
        "definitions": {
            object_class.__name__: serialize(object_class)
            for object_class in object_classes
            if object_class is not primary
        },
    }
    if definitions:
        schema["definitions"].update(
            {key: serialize(element) for key, element in definitions.items()}
        )
    if not schema["definitions"]:
        del schema["definitions"]
    return schema


def _serialize_element(
    element: Element,
    object_refs: bool = False,
    definitions: Dict[str, Any] = None,
):
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
            prop.source or name
            for name, prop in schema["properties"].items()
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
    return _serialize_recursive(
        schema, object_refs=object_refs, definitions=definitions
    )


_TYPE_MAPPING = {
    Array: "array",
    Boolean: "boolean",
    Integer: "integer",
    Null: "null",
    ObjectMeta: "object",
    Number: "number",
    String: "string",
}


def _serialize_recursive(
    data: Any, object_refs: bool = False, definitions: Dict[str, Element] = None
) -> Any:
    """Recursively serialize DSL elements."""
    recur = partial(
        _serialize_recursive, object_refs=object_refs, definitions=definitions
    )
    if isinstance(data, _Property):
        data = data.element
    if isinstance(data, ObjectMeta) and object_refs:
        return {"$ref": f"#/definitions/{data.__name__}"}
    if isinstance(data, Element):
        return _from_definitions(
            definitions,
            data,
            _serialize_element(
                data, object_refs=object_refs, definitions=definitions
            ),
        )
    if not isinstance(data, (list, dict)):
        return data
    if isinstance(data, list):
        return [recur(item) for item in data]
    return {key: recur(value) for key, value in data.items()}


def _from_definitions(
    definitions: Optional[Dict[str, Element]],
    element: Element,
    default: Any = None,
):
    """Check if this element is present in definitions."""
    if not definitions:
        return default
    return next(
        (
            {"$ref": f"#/definitions/{key}"}
            for key, definition in definitions.items()
            if definition == element
        ),
        default,
    )
