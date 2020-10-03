from typing import Any, List, TypeVar, Union

from statham.schema.elements.base import Element
from statham.schema.constants import Maybe, NotPassed
from statham.schema.validation import InstanceOf


T = TypeVar("T", int, float)

Numeric = Union[int, float]


# pylint: disable=too-many-instance-attributes
class NumericElement(Element[T]):
    """JSON Schema base numeric element."""

    def __init__(
        self,
        *,
        default: Maybe[T] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
        minimum: Maybe[Numeric] = NotPassed(),
        maximum: Maybe[Numeric] = NotPassed(),
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
    ):
        self.default = default
        self.const = const
        self.enum = enum
        self.minimum = minimum
        self.maximum = maximum
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf


class Integer(NumericElement[int]):
    """JSON Schema ``"integer"`` element.

    Accepts only python `int`.
    """

    @property
    def type_validator(self):
        return InstanceOf(int)


class Number(NumericElement[float]):
    """JSON Schema ``"number"`` element.

    Accepts python ``int`` or ``float``.
    """

    def construct(self, value, _property):  # pylint: disable=no-self-use
        return float(value)

    @property
    def type_validator(self):
        return InstanceOf(float, int)
