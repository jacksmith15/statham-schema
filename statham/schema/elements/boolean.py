from typing import Any, List

from statham.schema.elements.base import Element
from statham.schema.constants import Maybe, NotPassed
from statham.schema.validation import InstanceOf


class Boolean(Element[bool]):
    """JSON Schema ``"boolean"`` element."""

    def __init__(
        self,
        *,
        default: Maybe[bool] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
    ):
        self.default = default
        self.const = const
        self.enum = enum

    @property
    def type_validator(self):
        return InstanceOf(bool)
