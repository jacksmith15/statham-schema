from typing import Dict

from statham.dsl.constants import JSONElement


class StathamError(Exception):
    """Base exception"""


class SchemaDefinitionError(StathamError):
    """Failure when declaring schemas using DSL."""

    @classmethod
    def reserved_attribute(cls, attribute_name: str) -> "SchemaDefinitionError":
        # TODO: Default to underscore after not before.
        return cls(
            f"May not use reserved attribute `{attribute_name}` as a property "
            "attribute name. Instead use "
            f"`_{attribute_name} = Property(<element>, "
            f"source='{attribute_name}'`"
        )


class ValidationError(StathamError):
    """Validation failure in generated models."""

    @classmethod
    def from_validator(cls, property_, value, message) -> "ValidationError":
        return cls(
            f"Failed validating `{repr(property_.parent)}."
            f"{property_.name} = {repr(value)}`. {message}"
        )

    @classmethod
    def combine(
        cls, property_, value, exceptions, message
    ) -> "ValidationError":
        base_message = str(cls.from_validator(property_, value, ""))
        error_breakdown = ", ".join(str(exc) for exc in exceptions)
        error_breakdown = error_breakdown.replace(base_message, "")
        return cls.from_validator(
            property_, value, message + f" Individual errors: {error_breakdown}"
        )

    @classmethod
    def multiple_composition_match(cls, matching_models, data):
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

    @classmethod
    def invalid_type(cls, value):
        return cls(f"Got invalid type keyword: {value}.")


class FeatureNotImplementedError(SchemaParseError):
    """Functionality not yet implemented."""

    @classmethod
    def unsupported_keywords(cls, keywords) -> "FeatureNotImplementedError":
        return cls(
            f"The following provided keywords are not supported: {keywords}"
        )
