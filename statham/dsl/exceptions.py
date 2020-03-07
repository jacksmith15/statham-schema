from typing import Dict

from statham.dsl.constants import JSONElement


class StathamError(Exception):
    """Base exception"""


class ValidationError(StathamError):
    """Validation failure in generated models."""

    @classmethod
    def from_validator(cls, property_, value, message) -> "ValidationError":
        return cls(
            f"Failed validating `{repr(property_.parent)}."
            f"{property_.name} = {repr(value)}`. {message}"
        )

    @classmethod
    def mutliple_composition_match(cls, matching_models, data):
        return cls(
            "Matches multiple possible models. Must only match one.\n"
            f"Data: {data}\n"
            f"Models: {matching_models}"
        )


class SchemaParseError(StathamError):
    """Failure during parsing of provided JSON Schema input."""

    @classmethod
    def missing_title(
        cls, schema: Dict[str, JSONElement]
    ) -> "SchemaParseError":
        return cls(
            "No title defined in schema. Use "
            "`statham.titles.title_labeller` to pre-process the "
            f"schema: {schema}"
        )

    @classmethod
    def unresolvable_declaration(cls) -> "SchemaParseError":
        return cls(
            "Schema document has an unresolvable declaration tree. This "
            "generally occurs due to cyclical references."
        )
