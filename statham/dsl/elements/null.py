from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed


class Null(Element[None]):
    """JSONSchema null element."""

    def __init__(self, *, default: Maybe[None] = NotPassed()):
        self.default = default

    @property
    def annotation(self) -> str:
        return "None"

    @property
    def type_validator(self):
        return val.instance_of(type(None))
