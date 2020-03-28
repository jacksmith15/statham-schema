from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


class Boolean(Element[bool]):
    """JSONSchema boolean element."""

    def __init__(self, *, default: Maybe[bool] = NotPassed()):
        self.default = default

    @property
    def type_validator(self):
        return InstanceOf(bool)
