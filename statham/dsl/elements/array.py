from typing import List, TypeVar

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed


Item = TypeVar("Item")


class Array(Element[List[Item]]):
    """JSONSchema array element.

    Requires schema element for "items" keyword as first positional
    argument. Supported validation keywords provided via keyword arguments.
    # TODO: tuple items
    # TODO: additionalItems
    # TODO: unqiueItems
    # TODO: contains
    """

    def __init__(
        self,
        items: Element[Item],
        *,
        default: Maybe[List[Item]] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
    ):
        self.items = items
        self.default = default
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minItems = minItems
        self.maxItems = maxItems

    @property
    def annotation(self) -> str:
        return f"List[{self.items.annotation}]"

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

    def construct(self, value, property_):
        return [
            self.items(item, property_.evolve(property_.name + f"[{idx}]"))
            for idx, item in enumerate(value)
        ]
