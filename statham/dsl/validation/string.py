import re
from typing import Any

from statham.dsl.exceptions import ValidationError
from statham.dsl.validation.base import Validator
from statham.dsl.validation.format import format_checker


class Pattern(Validator):
    """Validate that string values match a regular expression."""

    types = (str,)
    keywords = ("pattern",)
    message = "Must match regex pattern {pattern}."

    def error_message(self):
        return self.message.format(pattern=repr(self.params["pattern"]))

    def _validate(self, value: Any):
        if not re.search(self.params["pattern"], value):
            raise ValidationError


class MinLength(Validator):
    """Validate that string values are over a minimum length."""

    types = (str,)
    keywords = ("minLength",)
    message = "Must be at least {minLength} characters long."

    def _validate(self, value: Any):
        if len(value) < self.params["minLength"]:
            raise ValidationError


class MaxLength(Validator):
    """Validate that string values are under a maximum length."""

    types = (str,)
    keywords = ("maxLength",)
    message = "Must be at most {maxLength} characters long."

    def _validate(self, value: Any):
        if len(value) > self.params["maxLength"]:
            raise ValidationError


class Format(Validator):
    """Validate that string values match a named format.

    Additional formats may be registered via
    :func:`~statham.dsl.validation.format.format_checker`.
    """

    types = (str,)
    keywords = ("format",)
    message = "Must match format described by '{format}'."

    def _validate(self, value: Any):
        if not format_checker(self.params["format"], value):
            raise ValidationError
