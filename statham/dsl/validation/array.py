from typing import Any

from statham.dsl.exceptions import ValidationError
from statham.dsl.validation.base import Validator


class MinItems(Validator):
    types = (list,)
    keywords = ("minItems",)
    message = "Must contain at least {minItems} items."

    def validate(self, value: Any):
        if len(value) < self.params["minItems"]:
            raise ValidationError


class MaxItems(Validator):
    types = (list,)
    keywords = ("maxItems",)
    message = "Must contain fewer than {maxItems} items."

    def validate(self, value: Any):
        if len(value) > self.params["maxItems"]:
            raise ValidationError


class AdditionalItems(Validator):
    types = (list,)
    keywords = ("items", "additionalItems")
    message = "Must not contain additional items. Accepts: {items}"

    def validate(self, value: Any):
        if not isinstance(self.params["items"], list):
            return
        if len(value) <= len(self.params["items"]):
            return
        if self.params["additionalItems"]:
            return
        raise ValidationError
