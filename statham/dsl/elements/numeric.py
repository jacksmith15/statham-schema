from typing import List, TypeVar, Union

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed


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
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        exclusiveMinimum: Maybe[Numeric] = NotPassed(),
        exclusiveMaximum: Maybe[Numeric] = NotPassed(),
        multipleOf: Maybe[Numeric] = NotPassed(),
    ):
        self.default = default
        self.minimum = minimum
        self.maximum = maximum
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.exclusiveMinimum = exclusiveMinimum
        self.exclusiveMaximum = exclusiveMaximum
        self.multipleOf = multipleOf

    @property
    def validators(self):
        validators: List[val.Validator] = super().validators
        if not isinstance(self.minimum, NotPassed):
            validators.append(val.minimum(self.minimum))
        if not isinstance(self.maximum, NotPassed):
            validators.append(val.maximum(self.maximum))
        if not isinstance(self.exclusiveMinimum, NotPassed):
            validators.append(val.exclusive_minimum(self.exclusiveMinimum))
        if not isinstance(self.exclusiveMaximum, NotPassed):
            validators.append(val.exclusive_maximum(self.exclusiveMaximum))
        if not isinstance(self.multipleOf, NotPassed):
            validators.append(val.multiple_of(self.multipleOf))
        return validators


class Integer(NumericElement[int]):
    """JSONSchema integer element.

    Provides supported validation settings via keyword arguments.
    """

    @property
    def annotation(self) -> str:
        return "int"

    @property
    def type_validator(self):
        return val.instance_of(int)


class Number(NumericElement[float]):
    """JSONSchema number element.

    Provides supported validation settings via keyword arguments.
    """

    @property
    def annotation(self) -> str:
        return "float"

    @property
    def type_validator(self):
        return val.instance_of(float)
