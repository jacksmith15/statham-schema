from typing import Dict, Set, Type

from jsonschema_objects.constants import JSONElement


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
        return cls(f"Not type defined in schema: {schema}")

    @classmethod
    def unsupported_type_union(
        cls, invalid: Set, requested: Set
    ) -> "SchemaParseError":
        return cls(
            f"Can't produce a union for these types: {invalid}. "
            f"The following union was requested: {requested}"
        )

    @classmethod
    def unresolvable_pointer(cls, reference: str) -> "SchemaParseError":
        return cls(f"Couldn't resolve JSON pointer: {reference}")

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


class NotImplementedSchemaParserError(SchemaParseError):
    """Failure parsing valid JSON Schema input which is not supported by this project."""

    @classmethod
    def remote_refs(cls) -> "SchemaParseError":
        return cls(
            "Remote references are not yet supported. Please see "
            "project homepage for more information."
        )

    @classmethod
    def non_object_refs(cls) -> "SchemaParseError":
        return cls("Only refs to object schemas are currently supported.")
