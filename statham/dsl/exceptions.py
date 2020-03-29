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
    def composite(cls, property_, value, messages) -> "ValidationError":
        base_message = str(cls.from_validator(property_, value, ""))
        message = ", ".join(messages)
        message = message.replace(base_message, "")
        return cls.from_validator(
            property_,
            value,
            f"Does not match any accepted schema. Individual errors: {message}",
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

    @classmethod
    def invalid_type(cls, value):
        return cls(f"Got invalid type keyword: {value}.")


class FeatureNotImplementedError(SchemaParseError):
    """Functionality not yet implemented."""

    @classmethod
    def multiple_composition_keywords(cls) -> "FeatureNotImplementedError":
        return cls(
            "Schema has multiple composition keywords. "
            "This is not yet supported."
        )

    @classmethod
    def tuple_array_items(cls) -> "FeatureNotImplementedError":
        return cls("Tuple array items are not supported.")
