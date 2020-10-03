from typing import Any, List, TypeVar, Union

from statham.schema.constants import Maybe, NotPassed
from statham.schema.elements.base import Element
from statham.schema.helpers import remove_duplicates
from statham.schema.validation import InstanceOf


Item = TypeVar("Item")


# pylint: disable=too-many-instance-attributes
class Array(Element[List[Item]]):  # pylint: disable=missing-param-doc
    """JSON Schema ``"array"`` element.

    :param items:
        As in :class:`statham.schema.elements.Element`, but as a required
        positional argument.
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
