from typing import List, TypeVar, Union

from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


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

    items: Union[Element[Item], List[Element[Item]]]

    def __init__(
        self,
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        items: Union[Element[Item], List[Element[Item]]],
        *,
        additionalItems: Union[Element[Item], bool] = True,
        default: Maybe[List[Item]] = NotPassed(),
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
    ):
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.items = items
        self.additionalItems = additionalItems
        self.default = default
        self.minItems = minItems
        self.maxItems = maxItems

    @property
    def annotation(self) -> str:
        if isinstance(self.items, Element):
            return f"List[{self.items.annotation}]"
        annotations = ", ".join(item.annotation for item in self.items)
        return f"List[Union[{annotations}]]"

    @property
    def type_validator(self):
        return InstanceOf(list)
