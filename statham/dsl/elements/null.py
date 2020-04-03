from typing import Any

from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


class Null(Element[None]):
    """JSONSchema null element."""

    def __init__(
        self,
        *,
        default: Maybe[None] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
    ):
        self.default = default
        self.const = const

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def type_validator(self):
        return InstanceOf(type(None))
