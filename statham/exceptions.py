import json
from typing import Dict, Set

from statham.constants import JSONElement


class JSONSchemaObjectError(Exception):
    """Base exception"""


class ValidationError(JSONSchemaObjectError):
    """Validation failure in generated models."""

    @classmethod
    def from_validator(
        cls, instance, attribute, value, message
    ) -> "ValidationError":
        return cls(
            f"Failed validating `{type(instance).__name__}."
            f"{attribute.name} = {repr(value)}`. {message}"
        )

    @classmethod
    def from_composition(cls, models, data) -> "ValidationError":
        return cls(
            f"Does not match any accepted model.\n"
            f"Data: {data}\n"
            f"Models: {models}"
        )


class SchemaParseError(JSONSchemaObjectError):
    """Failure during parsing of provided JSON Schema input."""

    @classmethod
    def missing_type(cls, schema: Dict[str, JSONElement]) -> "SchemaParseError":
        return cls(f"No type defined in schema: {json.dumps(schema, indent=2)}")

    @classmethod
    def unsupported_type_union(
        cls, invalid: Set, requested: Set
    ) -> "SchemaParseError":
        return cls(
            f"Can't produce a union for these types: {invalid}. "
            f"The following union was requested: {requested}"
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
            f"{str(exception)}:\nSchema: {json.dumps(schema, indent=2)}"
        )

    @classmethod
    def invalid_composition_schema(cls, schema) -> "SchemaParseError":
        return cls(
            "Failed to parse schema with composition keyword:\n"
            f"Schema: {json.dumps(schema, indent=2)}"
        )
