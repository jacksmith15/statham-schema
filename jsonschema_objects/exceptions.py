class JSONSchemaObjectError(Exception):
    """Base exception"""


class ValidationError(JSONSchemaObjectError):
    """Validation failure in generated models."""

    def __init__(self, instance, attribute, value, message=None) -> None:
        super().__init__(
            f"Failed validating `{type(instance)}.{attribute.name} = "
            f"{repr(value)}`. {message}"
        )
