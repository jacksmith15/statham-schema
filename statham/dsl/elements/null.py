from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


class Null(Element[None]):
    """JSONSchema null element."""

    def __init__(self, *, default: Maybe[None] = NotPassed()):
        self.default = default

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def type_validator(self):
        return InstanceOf(type(None))
