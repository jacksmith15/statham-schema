from typing import Any, List, TypeVar, Union

from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.elements.base import Element
from statham.dsl.helpers import remove_duplicates
from statham.dsl.validation import InstanceOf


Item = TypeVar("Item")


# pylint: disable=too-many-instance-attributes
class Array(Element[List[Item]]):
    """JSONSchema array element.

    Requires schema element for "items" keyword as first positional
    argument. Supported validation keywords provided via keyword arguments.
    """

    items: Union[Element[Item], List[Element]]

    def __init__(
        self,
        items: Union[Element[Item], List[Element]],
        *,
        default: Maybe[List] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
        additionalItems: Union[Element, bool] = True,
        minItems: Maybe[int] = NotPassed(),
        maxItems: Maybe[int] = NotPassed(),
        uniqueItems: bool = False,
        contains: Maybe[Element] = NotPassed(),
    ):
        self.items = items
        self.default = default
        self.const = const
        self.enum = enum
        self.additionalItems = additionalItems
        self.minItems = minItems
        self.maxItems = maxItems
        self.uniqueItems = uniqueItems
        self.contains = contains

    @property
    def annotation(self) -> str:
        if not self.item_annotations:
            return "List"
        if len(self.item_annotations) == 1:
            return f"List[{self.item_annotations[0]}]"
        return f"List[Union[{', '.join(self.item_annotations)}]]"

    @property
    def item_annotations(self) -> List[str]:
        """Get a list of possible type annotations."""
        if isinstance(self.items, Element):
            return [self.items.annotation]
        annotations: List[str] = [item.annotation for item in self.items]
        if self.additionalItems is True:
            return ["Any"]
        if isinstance(self.additionalItems, Element):
            annotations.append(self.additionalItems.annotation)
        if "Any" in annotations:
            return ["Any"]
        return remove_duplicates(annotations)

    @property
    def type_validator(self):
        return InstanceOf(list)
