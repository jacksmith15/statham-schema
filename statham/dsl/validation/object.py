from typing import Any, Optional

from statham.dsl.constants import NotPassed
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
    keywords = ("properties", "additionalProperties")
    message = "Must not contain unspecified properties. Accepts: {properties}"

    @classmethod
    def from_element(cls, element) -> Optional["AdditionalProperties"]:
        params = list(
            getattr(element, keyword, None) for keyword in cls.keywords
        )
        if None in params:
            return None
        params[0] = set(params[0] or {})
        params[1] = bool(
            True if isinstance(params[1], NotPassed) else params[1]
        )
        return cls(*params)

    def validate(self, value: Any):
        if self.params["additionalProperties"]:
            return
        if set(value) - self.params["properties"]:
            raise ValidationError
