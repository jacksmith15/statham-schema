from typing import List

from statham.dsl import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import Maybe, NotPassed


class String(Element[str]):
    """JSONSchema string element.

    Provides supported validation settings via keyword arguments.
    """

    def __init__(
        self,
        *,
        default: Maybe[str] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        format: Maybe[str] = NotPassed(),
        # pylint: enable=redefined-builtin
        pattern: Maybe[str] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minLength: Maybe[int] = NotPassed(),
        maxLength: Maybe[int] = NotPassed(),
    ):
        self.default = default
        self.format = format
        self.pattern = pattern
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minLength = minLength
        self.maxLength = maxLength

    @property
    def annotation(self) -> str:
        return "str"

    @property
    def type_validator(self):
        return val.instance_of(str)

    @property
    def validators(self):
        validators: List[val.Validator] = super().validators
        if not isinstance(self.format, NotPassed):
            validators.append(val.has_format(self.format))
        if not isinstance(self.pattern, NotPassed):
            validators.append(val.pattern(self.pattern))
        if not isinstance(self.minLength, NotPassed):
            validators.append(val.min_length(self.minLength))
        if not isinstance(self.maxLength, NotPassed):
            validators.append(val.max_length(self.maxLength))
        return validators
