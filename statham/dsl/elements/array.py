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
        items: Union[Element[Item], List[Element[Item]]],
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
        if isinstance(self.items, Element):
            return f"List[{self.items.annotation}]"
        annotations = ", ".join(item.annotation for item in self.items)
        return f"List[Union[{annotations}]]"

    @property
    def type_validator(self):
        return InstanceOf(list)

    def construct(self, value, property_):
        get_prop = lambda idx: property_.evolve(property_.name + f"[{idx}]")
        if isinstance(self.items, Element):
            return [
                self.items(item, get_prop(idx))
                for idx, item in enumerate(value)
            ]
        num_items = len(self.items)
        return [
            elem(value, get_prop(idx))
            for idx, (elem, value) in enumerate(zip(self.items, value))
        ] + [
            self.construct_additional(item, get_prop(idx))
            for idx, item in enumerate(value[num_items:], start=num_items)
        ]
