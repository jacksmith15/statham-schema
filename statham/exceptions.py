import json
from typing import Dict, Set

from statham.constants import JSONElement


class JSONSchemaObjectError(Exception):
    """Base exception"""


class ValidationError(JSONSchemaObjectError):
    """Validation failure in generated models."""

    def __init__(self, instance, attribute, value, message) -> None:
        super().__init__(
            f"Failed validating `{type(instance).__name__}."
            f"{attribute.name} = {repr(value)}`. {message}"
        )


class SchemaParseError(JSONSchemaObjectError):
    """Failure during parsing of provided JSON Schema input."""

    @classmethod
    def missing_type(cls, schema: Dict[str, JSONElement]) -> "SchemaParseError":
        return cls(f"No type defined in schema: {schema}")

    @classmethod
    def unsupported_type_union(
        cls, invalid: Set, requested: Set
    ) -> "SchemaParseError":
        return cls(
            f"Can't produce a union for these types: {invalid}. "
            f"The following union was requested: {requested}"
        )

    @classmethod
    def no_class_equivalent_schemas(cls) -> "SchemaParseError":
        return cls(
            "Schema document contains no object schemas from which to "
            "derive a class."
        )

    @classmethod
    def unresolvable_declaration(cls) -> "SchemaParseError":
        return cls(
            "Schema document has an unresolvable declaration tree. This "
            "generally occurs due to cyclical references."
        )

    @classmethod
    def from_exception(
        cls, schema: Dict[str, JSONElement], exception: Exception
    ) -> "SchemaParseError":
        return cls(
            "Failed to parse the following schema:\nError: "
            f"{str(exception)}:\nSchema: {json.dumps(schema)}"
        )
