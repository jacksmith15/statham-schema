from typing import Any, cast, Optional

from statham.dsl.exceptions import ValidationError
from statham.dsl.helpers import remove_duplicates
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


class UniqueItems(Validator):
    types = (list,)
    keywords = ("uniqueItems",)
    message = "Must not contain duplicates."

    @classmethod
    def from_element(cls, element) -> Optional["UniqueItems"]:
        validator: Optional[UniqueItems] = cast(
            Optional[UniqueItems], super().from_element(element)
        )
        if validator and validator.params["uniqueItems"] is False:
            return None
        return validator

    def validate(self, value: Any):
        # Once again, Cpython's 1 in [True] nightmare.
        true = object()
        false = object()
        alias = lambda x: true if x is True else false if x is False else x
        aliased_value = list(map(alias, value))
        length = len(aliased_value)
        try:
            # Try the hashable approach
            if len(set(aliased_value)) == length:
                return
        except TypeError:
            # Long version
            if len(remove_duplicates(aliased_value)) == length:
                return
        raise ValidationError


class Contains(Validator):
    types = (list,)
    keywords = ("contains",)
    message = "Must contain one element matching {contains}."

    def validate(self, value: Any):
        for sub_value in value:
            try:
                _ = self.params["contains"](sub_value)
                return
            except (TypeError, ValidationError):
                continue
        raise ValidationError
