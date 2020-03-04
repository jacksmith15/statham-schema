from typing import Any, List, Union

from statham import validators as val
from statham.dsl.elements.base import Element
from statham.dsl.constants import NotPassed


class String(Element):
    """JSONSchema string element.

    Provides supported validation settings via keyword arguments.
    """

    def __init__(
        self,
        *,
        default: Any = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=redefined-builtin
        format: Union[str, NotPassed] = NotPassed(),
        # pylint: enable=redefined-builtin
        pattern: Union[str, NotPassed] = NotPassed(),
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        minLength: Union[int, NotPassed] = NotPassed(),
        maxLength: Union[int, NotPassed] = NotPassed(),
    ):
        self.default = default
        self.format = format
        self.pattern = pattern
        # Bad name to match JSONSchema keywords.
        # pylint: disable=invalid-name
        self.minLength = minLength
        self.maxLength = maxLength

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
