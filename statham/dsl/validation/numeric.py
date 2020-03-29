from typing import Any
from statham.dsl.exceptions import ValidationError
from statham.dsl.validation.base import Validator


class Minimum(Validator):
    types = (int, float)
    keywords = ("minimum",)
    message = "Must be greater than or equal to {minimum}."

    def validate(self, value: Any):
        if value < self.params["minimum"]:
            raise ValidationError


class Maximum(Validator):
    types = (int, float)
    keywords = ("maximum",)
    message = "Must be less than or equal to {maximum}."

    def validate(self, value: Any):
        if value > self.params["maximum"]:
            raise ValidationError


class ExclusiveMinimum(Validator):
    types = (int, float)
    keywords = ("exclusiveMinimum",)
    message = "Must be strictly greater than {exclusiveMinimum}."

    def validate(self, value: Any):
        if value <= self.params["exclusiveMinimum"]:
            raise ValidationError


class ExclusiveMaximum(Validator):
    types = (int, float)
    keywords = ("exclusiveMaximum",)
    message = "Must be strictly less than {exclusiveMaximum}."

    def validate(self, value: Any):
        if value >= self.params["exclusiveMaximum"]:
            raise ValidationError


class MultipleOf(Validator):
    types = (int, float)
    keywords = ("multipleOf",)
    message = "Must be a multiple of {multipleOf}."

    def validate(self, value: Any):
        if value % self.params["multipleOf"]:
            raise ValidationError
