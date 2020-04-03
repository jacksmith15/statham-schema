from typing import TypeVar, Union

from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


T = TypeVar("T", int, float)

Numeric = Union[int, float]


class NumericElement(Element[T]):
    """JSONSchema base numeric element.

    Provides supported validation settings via keyword arguments.
    """

    def __init__(
        self,
        *,
        default: Maybe[T] = NotPassed(),
        minimum: Maybe[Numeric] = NotPassed(),
        maximum: Maybe[Numeric] = NotPassed(),
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
    ):
        self.default = default
        self.minimum = minimum
        self.maximum = maximum
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf


class Integer(NumericElement[int]):
    """JSONSchema integer element.

    Provides supported validation settings via keyword arguments.
    """

    @property
    def type_validator(self):
        return InstanceOf(int)


class Number(NumericElement[float]):
    """JSONSchema number element.

    Provides supported validation settings via keyword arguments.
    """

    def construct(self, value, _property):  # pylint: disable=no-self-use
        return float(value)

    @property
    def type_validator(self):
        return InstanceOf(float, int)
