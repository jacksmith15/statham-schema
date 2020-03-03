from typing import Union

from statham import validators as val
from statham.dsl.elements.base import Element
from statham.validators import NotPassed


class Array(Element):
    """JSONSchema array element.

    Requires schema element for "items" keyword as first positional
    argument. Supported validation keywords provided via keyword arguments.
    """

    def __init__(
        self,
        items: Element,
        *,
        required: bool = False,
        default: Union[list, NotPassed] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minItems: Union[int, NotPassed] = NotPassed(),
        maxItems: Union[int, NotPassed] = NotPassed(),
    ):
        self.items = items
        self.required = required
        self.default = default
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minItems = minItems
        self.maxItems = maxItems

    @property
    def type_validator(self):
        return val.instance_of(list)

    @property
    def validators(self):
        validators = super().validators
        if not isinstance(self.minItems, NotPassed):
            validators.append(val.min_items(self.minItems))
        if not isinstance(self.maxItems, NotPassed):
            validators.append(val.max_items(self.maxItems))
        return validators

    def construct(self, instance, attribute, value):
        return [
            self.items(
                instance, val.Attribute(attribute.name + f"[{idx}]"), item
            )
            for idx, item in enumerate(value)
        ]