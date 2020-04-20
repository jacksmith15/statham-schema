from typing import Any, List

from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


class Null(Element[None]):
    """JSON Schema ``"null"`` element."""

    def __init__(
        self,
        *,
        default: Maybe[None] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
    ):
        self.default = default
        self.const = const
        self.enum = enum

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def type_validator(self):
        return InstanceOf(type(None))
