from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed


class Boolean(Element[bool]):
    """JSONSchema boolean element."""

    def __init__(self, *, default: Maybe[bool] = NotPassed()):
        self.default = default

    @property
    def annotation(self) -> str:
        return "bool"

    @property
    def type_validator(self):
        return val.instance_of(bool)
