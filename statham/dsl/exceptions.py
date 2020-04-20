from typing import Dict

from statham.dsl.constants import JSONElement


class StathamError(Exception):
    """Base exception for errors relating to :mod:`statham`."""


class SchemaDefinitionError(StathamError):
    """Raised when invalid schemas are declared in the DSL."""

    @classmethod
    def reserved_attribute(cls, attribute_name: str) -> "SchemaDefinitionError":
        return cls(
            f"May not use reserved attribute `{attribute_name}` as a property "
            "attribute name. Instead use "
            f"`{attribute_name}_ = Property(<element>, "
            f"source='{attribute_name}'`"
        )


class ValidationError(StathamError):
    """Raised when JSON Schema validation fails for input data."""

    @classmethod
    def from_validator(cls, property_, value, message) -> "ValidationError":
        value_string = (
            f"{repr(property_.parent)}{property_.name} = {repr(value)}`"
            if property_.name != "<unbound>"
            else repr(value)
        )
        return cls(f"Failed validating `{value_string}`. {message}")

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
    """Raised when parsing JSON Schema documents to DSL objects."""

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


# pylint: disable=line-too-long
class FeatureNotImplementedError(SchemaParseError):
    """Raised when parsing valid JSON Schema features currently unsupported by the DSL."""

    @classmethod
    def unsupported_keywords(cls, keywords) -> "FeatureNotImplementedError":
        return cls(
            f"The following provided keywords are not supported: {keywords}"
        )
