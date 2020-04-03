from typing import Any, List

from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed
from statham.dsl.validation import InstanceOf


class String(Element[str]):
    """JSONSchema string element.

    Provides supported validation settings via keyword arguments.
    """

    def __init__(
        self,
        *,
        default: Maybe[str] = NotPassed(),
        const: Maybe[Any] = NotPassed(),
        enum: Maybe[List[Any]] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        format: Maybe[str] = NotPassed(),
        # pylint: enable=redefined-builtin
        pattern: Maybe[str] = NotPassed(),
        minLength: Maybe[int] = NotPassed(),
        maxLength: Maybe[int] = NotPassed(),
    ):
        self.default = default
        self.const = const
        self.enum = enum
        self.format = format
        self.pattern = pattern
        self.minLength = minLength
        self.maxLength = maxLength

    @property
    def type_validator(self):
        return InstanceOf(str)
