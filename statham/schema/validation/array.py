from typing import Any, cast, Optional

from statham.schema.exceptions import ValidationError
from statham.schema.helpers import remove_duplicates
from statham.schema.validation.base import Validator, replace_bool


class MinItems(Validator):
    """Validate that arrays have a minimum number of items."""

    types = (list,)
    keywords = ("minItems",)
    message = "Must contain at least {minItems} items."

    def _validate(self, value: Any):
        if len(value) < self.params["minItems"]:
            raise ValidationError


class MaxItems(Validator):
    """Validate that arrays have a maximum number of items."""

    types = (list,)
    keywords = ("maxItems",)
    message = "Must contain fewer than {maxItems} items."

    def _validate(self, value: Any):
        if len(value) > self.params["maxItems"]:
            raise ValidationError


class AdditionalItems(Validator):
    """Validate array items not covered by the ``"items"`` keyword.

    Only relevant when using "tuple" style ``"items"``.
    """

    types = (list,)
    keywords = ("items", "additionalItems")
    message = "Must not contain additional items. Accepts: {items}"

    def _validate(self, value: Any):
        if not isinstance(self.params["items"], list):
            return
        if len(value) <= len(self.params["items"]):
            return
        if self.params["additionalItems"]:
            return
        raise ValidationError


class UniqueItems(Validator):
    """Validate that array items are unique."""

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

    def _validate(self, value: Any):
        # Once again, Cpython's 1 in [True] nightmare.
        aliased_value = list(map(replace_bool, value))
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
    """Validate that at least one array item matches a schema."""

    types = (list,)
    keywords = ("contains",)
    message = "Must contain one element matching {contains}."

    def _validate(self, value: Any):
        for sub_value in value:
            try:
                _ = self.params["contains"](sub_value)
                return
            except (TypeError, ValidationError):
                continue
        raise ValidationError
