from typing import Any
from statham.schema.exceptions import ValidationError
from statham.schema.validation.base import Validator


class Minimum(Validator):
    """Validate that numeric values conform to a minimum."""

    types = (int, float)
    keywords = ("minimum",)
    message = "Must be greater than or equal to {minimum}."

    def _validate(self, value: Any):
        if value < self.params["minimum"]:
            raise ValidationError


class Maximum(Validator):
    """Validate that numeric values conform to a maximum."""

    types = (int, float)
    keywords = ("maximum",)
    message = "Must be less than or equal to {maximum}."

    def _validate(self, value: Any):
        if value > self.params["maximum"]:
            raise ValidationError


class ExclusiveMinimum(Validator):
    """Validate that numeric values conform to an exclusive minimum."""

    types = (int, float)
    keywords = ("exclusiveMinimum",)
    message = "Must be strictly greater than {exclusiveMinimum}."

    def _validate(self, value: Any):
        if value <= self.params["exclusiveMinimum"]:
            raise ValidationError


class ExclusiveMaximum(Validator):
    """Validate that numeric values conform to an exclusive maximum."""

    types = (int, float)
    keywords = ("exclusiveMaximum",)
    message = "Must be strictly less than {exclusiveMaximum}."

    def _validate(self, value: Any):
        if value >= self.params["exclusiveMaximum"]:
            raise ValidationError


class MultipleOf(Validator):
    """Validate that numeric values are a multiple of a given number."""

    types = (int, float)
    keywords = ("multipleOf",)
    message = "Must be a multiple of {multipleOf}."

    def _validate(self, value: Any):
        multiple_of = self.params["multipleOf"]
        if isinstance(multiple_of, float):
            quotient = value / multiple_of
            if int(quotient) != quotient:
                raise ValidationError
            return
        if value % multiple_of:
            raise ValidationError
