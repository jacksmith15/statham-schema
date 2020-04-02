from typing import Any

from statham.dsl.exceptions import ValidationError
from statham.dsl.validation.base import Validator


class Required(Validator):
    types = (dict,)
    keywords = ("required",)
    message = "Must contain all required fields: {required}"

    def validate(self, value: Any):
        if set(self.params["required"]) - set(value):
            raise ValidationError


class AdditionalProperties(Validator):
    types = (dict,)
    keywords = ("__properties__",)
    message = "Must not contain unspecified properties. Accepts: {properties}"

    def error_message(self):
        return self.message.format(
            properties=set(self.params["__properties__"])
        )

    def validate(self, value: Any):
        if self.params["__properties__"].additional:
            return
        bad_properties = {
            key for key in value if key not in self.params["__properties__"]
        }
        if bad_properties:
            raise ValidationError
